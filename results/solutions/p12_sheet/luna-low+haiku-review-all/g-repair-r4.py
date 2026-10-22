def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    tokens_re = re.compile(
        r"\s*(?:(\d+)|([A-Z](?:[1-9]\d?))|(SUM|MIN|MAX|IF)|"
        r"(<=|>=|<>|[+\-*/(),:=<>]))"
    )

    class Parser:
        def __init__(self, text):
            self.tokens = []
            pos = 0
            while pos < len(text):
                if not text[pos:].strip():
                    break
                match = tokens_re.match(text, pos)
                if not match:
                    raise ValueError("Invalid formula")
                number, cell, function, operator = match.groups()
                self.tokens.append(
                    number if number is not None else
                    cell if cell is not None else
                    function if function is not None else operator
                )
                pos = match.end()
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.i += 1
            return token

        def formula(self):
            node = self.term()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.term())
            return node

        def term(self):
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

            if token.isdigit():
                self.take()
                return ("num", int(token))

            if token == "(":
                self.take("(")
                node = self.formula()
                self.take(")")
                return node

            if token in ("SUM", "MIN", "MAX"):
                name = self.take()
                self.take("(")
                args = [self.function_arg()]
                while self.peek() == ",":
                    self.take(",")
                    args.append(self.function_arg())
                self.take(")")
                return ("func", name, args)

            if token == "IF":
                self.take("IF")
                self.take("(")
                left = self.formula()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid formula")
                right = self.formula()
                self.take(",")
                then = self.formula()
                self.take(",")
                otherwise = self.formula()
                self.take(")")
                return ("if", op, left, right, then, otherwise)

            self.take()
            return ("ref", token)

        def function_arg(self):
            first = self.peek()
            if first is not None and first[0].isalpha() and first != "IF":
                if self.i + 1 < len(self.tokens) and self.tokens[self.i + 1] == ":":
                    start = self.take()
                    self.take(":")
                    end = self.take()
                    return ("range", start, end)
            return ("expr", self.formula())

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parser = Parser(content[1:])
            parsed[name] = parser.formula()
            if parser.peek() is not None:
                raise ValueError("Invalid formula")
        else:
            parsed[name] = ("num", int(content))

    state = {}
    values = {}

    def coordinates(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    def cell_value(name):
        if name not in cells:
            return 0
        status = state.get(name, 0)
        if status == 1:
            return CYCLE
        if status == 2:
            return values[name]

        state[name] = 1
        value = evaluate(parsed[name])
        state[name] = 2
        values[name] = value
        return value

    def evaluate(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "ref":
            return cell_value(node[1])

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
            _, op, left_node, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right

            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(then_node if condition else else_node)

        if kind == "func":
            _, name, args = node
            aggregate = []
            for arg in args:
                if arg[0] == "expr":
                    value = evaluate(arg[1])
                    if isinstance(value, str):
                        return value
                    aggregate.append(value)
                else:
                    _, start, end = arg
                    c1, r1 = coordinates(start)
                    c2, r2 = coordinates(end)
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            cell = chr(ord("A") + col) + str(row + 1)
                            if cell in cells:
                                value = cell_value(cell)
                                if isinstance(value, str):
                                    return value
                                aggregate.append(value)

            if not aggregate:
                return 0
            if name == "SUM":
                return sum(aggregate)
            if name == "MIN":
                return min(aggregate)
            return max(aggregate)

        raise ValueError("Invalid formula")

    for name in cells:
        cell_value(name)

    return values
