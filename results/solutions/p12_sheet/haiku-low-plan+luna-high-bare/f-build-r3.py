def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    token_re = re.compile(r"\s*(<>|<=|>=|[A-Z][0-9]+|[A-Z]+|[0-9]+|[()+\-*/,:=<>])")

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                if text[pos:].strip() == "":
                    break
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.pos += 1
            return token

        def expr(self):
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
                self.take("-")
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            token = self.peek()
            if token == "(":
                self.take("(")
                node = self.expr()
                self.take(")")
                return node
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                self.take()
                return ("num", int(token))
            if token.isalpha():
                self.take()
                if self.peek() == "(":
                    self.take("(")
                    if token == "IF":
                        left = self.expr()
                        op = self.take()
                        if op not in ("=", "<>", "<", "<=", ">", ">="):
                            raise ValueError("Invalid formula")
                        right = self.expr()
                        self.take(",")
                        then_node = self.expr()
                        self.take(",")
                        else_node = self.expr()
                        self.take(")")
                        return ("if", left, op, right, then_node, else_node)

                    args = []
                    while True:
                        if (
                            self.peek() is not None
                            and re.fullmatch(r"[A-Z][0-9]+", self.peek())
                            and self.pos + 1 < len(self.tokens)
                            and self.tokens[self.pos + 1] == ":"
                        ):
                            first = self.take()
                            self.take(":")
                            second = self.take()
                            if not re.fullmatch(r"[A-Z][0-9]+", second):
                                raise ValueError("Invalid range")
                            args.append(("range", first, second))
                        else:
                            args.append(self.expr())
                        if self.peek() != ",":
                            break
                        self.take(",")
                    self.take(")")
                    return ("call", token, args)
                return ("ref", token)
            raise ValueError("Invalid formula")

        def parse(self):
            node = self.expr()
            if self.peek() is not None:
                raise ValueError("Invalid formula")
            return node

    ast_cache = {}
    state = {}
    IN_PROGRESS = object()

    def column_index(cell):
        return ord(cell[0]) - ord("A")

    def row_index(cell):
        return int(cell[1:])

    def parse_cell(name):
        if name not in ast_cache:
            content = cells[name]
            if isinstance(content, int):
                ast_cache[name] = ("num", content)
            elif content.startswith("="):
                ast_cache[name] = Parser(content[1:]).parse()
            else:
                ast_cache[name] = ("num", int(content))
        return ast_cache[name]

    def value(name):
        if name not in cells:
            return 0
        current = state.get(name)
        if current is IN_PROGRESS:
            return "#CYCLE!"
        if name in state:
            return current
        state[name] = IN_PROGRESS
        result = evaluate(parse_cell(name))
        state[name] = result
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return value(node[1])
        if kind == "neg":
            val = evaluate(node[1])
            return val if isinstance(val, str) else -val
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
                return "#DIV/0!"
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
            matches = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(then_node if matches else else_node)
        if kind == "call":
            _, fname, args = node
            values = []
            for arg in args:
                if arg[0] == "range":
                    _, first, second = arg
                    c1, c2 = sorted((column_index(first), column_index(second)))
                    r1, r2 = sorted((row_index(first), row_index(second)))
                    for row in range(r1, r2 + 1):
                        for col in range(c1, c2 + 1):
                            cell = chr(ord("A") + col) + str(row)
                            if cell in cells:
                                val = value(cell)
                                if isinstance(val, str):
                                    return val
                                values.append(val)
                else:
                    val = evaluate(arg)
                    if isinstance(val, str):
                        return val
                    values.append(val)

            if fname == "SUM":
                return sum(values)
            if not values:
                return 0
            if fname == "MIN":
                return min(values)
            if fname == "MAX":
                return max(values)
        raise ValueError("Invalid expression")

    return {name: value(name) for name in cells}
