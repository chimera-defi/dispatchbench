def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    ERR_DIV = "#DIV/0!"
    ERR_CYCLE = "#CYCLE!"
    tokens_re = re.compile(
        r"\s*(<=|>=|<>|[A-Za-z][0-9]{1,2}|[0-9]+|[()+\-*/,:=<>])"
    )

    def tokenize(s):
        tokens = []
        pos = 0
        while pos < len(s):
            match = tokens_re.match(s, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    formulas = {}
    for name, content in cells.items():
        if content.startswith("="):
            formulas[name] = tokenize(content[1:])

    values = {}
    active = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return ERR_CYCLE

        active.add(name)
        content = cells[name]
        if content.startswith("="):
            tokens = formulas[name]
            parser = Parser(tokens, cell_value)
            value = parser.parse()
        else:
            value = int(content)
        active.remove(name)
        values[name] = value
        return value

    class Parser:
        def __init__(self, tokens, get_cell):
            self.tokens = tokens
            self.i = 0
            self.get_cell = get_cell

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.i += 1
            return token

        def parse(self):
            return self.expression()

        def expression(self):
            value = self.term()
            while self.peek() in ("+", "-"):
                op = self.take()
                if isinstance(value, str):
                    return value
                right = self.term()
                if isinstance(right, str):
                    return right
                value = value + right if op == "+" else value - right
            return value

        def term(self):
            value = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                if isinstance(value, str):
                    return value
                right = self.unary()
                if isinstance(right, str):
                    return right
                if op == "*":
                    value *= right
                elif right == 0:
                    return ERR_DIV
                else:
                    quotient = abs(value) // abs(right)
                    value = -quotient if (value < 0) != (right < 0) else quotient
            return value

        def unary(self):
            if self.peek() == "-":
                self.take()
                value = self.unary()
                return value if isinstance(value, str) else -value
            return self.atom()

        def atom(self):
            token = self.take()
            if token == "(":
                value = self.expression()
                self.take()  # )
                return value
            if token is None:
                raise ValueError("Unexpected end")
            if token.isdigit():
                return int(token)
            if re.fullmatch(r"[A-Z][1-9][0-9]?", token):
                return self.get_cell(token)
            if token in ("SUM", "MIN", "MAX"):
                return self.aggregate(token)
            if token == "IF":
                return self.if_call()
            raise ValueError("Invalid atom")

        def aggregate(self, fn):
            self.take()  # (
            result = None
            while True:
                first = self.peek()
                if first is not None and re.fullmatch(r"[A-Z][1-9][0-9]?", first):
                    saved = self.i
                    start = self.take()
                    if self.peek() == ":":
                        self.take()
                        end = self.take()
                        for name in range_cells(start, end):
                            value = self.get_cell(name)
                            if isinstance(value, str):
                                return value
                            result = combine(fn, result, value)
                    else:
                        self.i = saved
                        value = self.expression()
                        if isinstance(value, str):
                            return value
                        result = combine(fn, result, value)
                else:
                    value = self.expression()
                    if isinstance(value, str):
                        return value
                    result = combine(fn, result, value)

                if self.peek() == ",":
                    self.take()
                else:
                    self.take()  # )
                    break
            return 0 if result is None else result

        def if_call(self):
            self.take()  # (
            left = self.expression()
            if isinstance(left, str):
                return left
            op = self.take()
            right = self.expression()
            if isinstance(right, str):
                return right
            self.take()  # ,
            then_value = self.expression()
            self.take()  # ,
            else_start = self.i

            # Parse the else expression only if selected; skip its tokens otherwise.
            if compare(left, op, right):
                self.take()  # )
                return then_value

            self.i = else_start
            else_value = self.expression()
            self.take()  # )
            return else_value

    def combine(fn, current, value):
        if current is None:
            return value
        if fn == "SUM":
            return current + value
        if fn == "MIN":
            return min(current, value)
        return max(current, value)

    def range_cells(start, end):
        c1, r1 = ord(start[0]) - 65, int(start[1:])
        c2, r2 = ord(end[0]) - 65, int(end[1:])
        for row in range(min(r1, r2), max(r1, r2) + 1):
            for col in range(min(c1, c2), max(c1, c2) + 1):
                yield chr(65 + col) + str(row)

    def compare(left, op, right):
        if op == "=":
            return left == right
        if op == "<>":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        return left >= right

    # Define the parser before evaluation, then evaluate every supplied cell.
    return {name: cell_value(name) for name in cells}
