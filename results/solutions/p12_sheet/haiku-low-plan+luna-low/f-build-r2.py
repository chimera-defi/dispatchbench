def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    state = {}
    values = {}
    asts = {}

    token_re = re.compile(r"\s+|(?:<>|<=|>=)|[A-Z](?:[1-9][0-9]?)|[0-9]+|[A-Za-z]+|.")

    def tokenize(text):
        return [m.group(0) for m in token_re.finditer(text) if not m.group(0).isspace()]

    def cell_parts(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.i += 1
            return token

        def parse(self):
            node = self.additive()
            if self.peek() is not None:
                raise ValueError("Invalid formula")
            return node

        def additive(self):
            node = self.multiplicative()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.multiplicative())
            return node

        def multiplicative(self):
            node = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.peek() == "-":
                self.take()
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            token = self.peek()
            if token is None:
                raise ValueError("Invalid formula")

            if token == "(":
                self.take("(")
                node = self.additive()
                self.take(")")
                return node

            if token.isdigit():
                self.take()
                return ("num", int(token))

            if re.fullmatch(r"[A-Z][1-9][0-9]?", token):
                self.take()
                return ("ref", token)

            if token in ("SUM", "MIN", "MAX"):
                self.take()
                self.take("(")
                args = []
                while True:
                    args.append(self.function_arg())
                    if self.peek() != ",":
                        break
                    self.take(",")
                self.take(")")
                return ("func", token, args)

            if token == "IF":
                self.take()
                self.take("(")
                left = self.additive()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid formula")
                right = self.additive()
                self.take(",")
                then_node = self.additive()
                self.take(",")
                else_node = self.additive()
                self.take(")")
                return ("if", left, op, right, then_node, else_node)

            raise ValueError("Invalid formula")

        def function_arg(self):
            first = self.peek()
            if (first is not None and
                    re.fullmatch(r"[A-Z][1-9][0-9]?", first) and
                    self.i + 1 < len(self.tokens) and
                    self.tokens[self.i + 1] == ":"):
                start = self.take()
                self.take(":")
                end = self.take()
                if not re.fullmatch(r"[A-Z][1-9][0-9]?", end):
                    raise ValueError("Invalid range")
                return ("range", start, end)
            return self.additive()

    def get(name):
        status = state.get(name)
        if status == 2:
            return values[name]
        if status == 1:
            return CYCLE

        content = cells.get(name)
        if content is None:
            return 0

        if not content.startswith("="):
            result = int(content)
            state[name] = 2
            values[name] = result
            return result

        state[name] = 1
        if name not in asts:
            asts[name] = Parser(content[1:]).parse()
        result = evaluate(asts[name])
        values[name] = result
        state[name] = 2
        return result

    def evaluate(node):
        kind = node[0]

        if kind == "num":
            return node[1]
        if kind == "ref":
            return get(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, left_node, op, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(then_node if comparisons[op] else else_node)
        if kind == "func":
            _, func, args = node
            collected = []
            for arg in args:
                if arg[0] == "range":
                    _, start, end = arg
                    c1, r1 = cell_parts(start)
                    c2, r2 = cell_parts(end)
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(ord("A") + col) + str(row + 1)
                            if name not in cells:
                                continue
                            value = get(name)
                            if isinstance(value, str):
                                return value
                            collected.append(value)
                else:
                    value = evaluate(arg)
                    if isinstance(value, str):
                        return value
                    collected.append(value)

            if not collected:
                return 0
            if func == "SUM":
                return sum(collected)
            if func == "MIN":
                return min(collected)
            return max(collected)

        raise ValueError("Invalid AST")

    return {name: get(name) for name in cells}
