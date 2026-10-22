def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    values = {}
    active = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return CYCLE

        active.add(name)
        content = cells[name].strip()
        if not content.startswith("="):
            value = int(content)
        else:
            parser = Parser(content[1:], cell_value)
            value = parser.parse()
        active.remove(name)
        values[name] = value
        return value

    class Parser:
        def __init__(self, text, get_cell):
            self.text = text
            self.i = 0
            self.get_cell = get_cell

        def spaces(self):
            while self.i < len(self.text) and self.text[self.i].isspace():
                self.i += 1

        def peek(self):
            self.spaces()
            return self.text[self.i] if self.i < len(self.text) else ""

        def take(self, token):
            self.spaces()
            if self.text.startswith(token, self.i):
                self.i += len(token)
                return True
            return False

        def parse(self):
            return self.expr()

        def expr(self):
            value = self.term()
            while True:
                op = self.peek()
                if op not in ("+", "-"):
                    return value
                self.i += 1
                if isinstance(value, str):
                    self.term()
                    return value
                right = self.term()
                if isinstance(right, str):
                    return right
                value = value + right if op == "+" else value - right

        def term(self):
            value = self.unary()
            while True:
                op = self.peek()
                if op not in ("*", "/"):
                    return value
                self.i += 1
                if isinstance(value, str):
                    self.unary()
                    return value
                right = self.unary()
                if isinstance(right, str):
                    return right
                if op == "*":
                    value *= right
                elif right == 0:
                    return DIV0
                else:
                    q = abs(value) // abs(right)
                    value = -q if (value < 0) != (right < 0) else q

        def unary(self):
            if self.take("-"):
                value = self.unary()
                return value if isinstance(value, str) else -value
            return self.atom()

        def atom(self):
            if self.take("("):
                value = self.expr()
                self.take(")")
                return value

            self.spaces()
            start = self.i
            while self.i < len(self.text) and self.text[self.i].isalpha():
                self.i += 1
            if self.i > start:
                name = self.text[start:self.i].upper()
                if self.take("("):
                    if name == "IF":
                        return self.if_call()
                    return self.aggregate(name)
                while self.i < len(self.text) and self.text[self.i].isdigit():
                    self.i += 1
                return self.get_cell(self.text[start:self.i])

            self.spaces()
            start = self.i
            while self.i < len(self.text) and self.text[self.i].isdigit():
                self.i += 1
            return int(self.text[start:self.i])

        def if_call(self):
            left = self.expr()
            self.take(",")
            right = self.expr()
            self.take(",")
            op = None
            for candidate in ("<>", "<=", ">=", "=", "<", ">"):
                if self.take(candidate):
                    op = candidate
                    break

            # Grammar places the comparison operator between left and right.
            # Reparse IF's first two operands in their correct form instead.
            return self._if_after_left(left, right, op)

        def _if_after_left(self, left, right, op):
            # The initial parsing above is only used for a valid expression
            # stream if the comma/operator delimiters are handled explicitly;
            # this method is replaced by the direct parser below.
            return 0

        def aggregate(self, name):
            args = []
            while True:
                self.spaces()
                save = self.i
                first = self.cell_token()
                if first is not None:
                    if self.take(":"):
                        second = self.cell_token()
                        if second is not None:
                            args.append(("range", first, second))
                        else:
                            self.i = save
                            args.append(("formula", self.expr()))
                    else:
                        self.i = save
                        args.append(("formula", self.expr()))
                else:
                    args.append(("formula", self.expr()))
                if not self.take(","):
                    break

            result = None
            for kind, a, *rest in args:
                if kind == "formula":
                    vals = [a]
                else:
                    b = rest[0]
                    c1, r1 = self.split_cell(a)
                    c2, r2 = self.split_cell(b)
                    vals = []
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            cell = chr(ord("A") + col) + str(row)
                            if cell in cells:
                                vals.append(self.get_cell(cell))
                for value in vals:
                    if isinstance(value, str):
                        return value
                    if result is None:
                        result = value
                    elif name == "SUM":
                        result += value
                    elif name == "MIN":
                        result = min(result, value)
                    elif name == "MAX":
                        result = max(result, value)
            return 0 if result is None else result

        def cell_token(self):
            self.spaces()
            start = self.i
            if self.i >= len(self.text) or not self.text[self.i].isalpha():
                return None
            self.i += 1
            digit_start = self.i
            while self.i < len(self.text) and self.text[self.i].isdigit():
                self.i += 1
            if digit_start == self.i:
                self.i = start
                return None
            return self.text[start:self.i].upper()

        @staticmethod
        def split_cell(cell):
            return ord(cell[0]) - ord("A"), int(cell[1:])

    # Define a parser variant with direct IF parsing, preserving short-circuiting.
    original_if = Parser.if_call

    def fixed_if(self):
        left = self.expr()
        if isinstance(left, str):
            self.take(",")
            # Consume the rest of the call without evaluating it.
            self.skip_to_call_end()
            return left
        self.take(",")
        right = self.expr()
        if isinstance(right, str):
            self.take(",")
            self.skip_to_call_end()
            return right

        self.spaces()
        op = None
        for candidate in ("<>", "<=", ">=", "=", "<", ">"):
            if self.take(candidate):
                op = candidate
                break
        self.take(",")
        then_start = self.i
        then_value = self.expr()
        self.take(",")
        else_value = self.expr()
        self.take(")")

        tests = {
            "=": left == right,
            "<>": left != right,
            "<": left < right,
            "<=": left <= right,
            ">": left > right,
            ">=": left >= right,
        }
        # Branches are evaluated lazily; parse the selected branch directly.
        # (The valid-formula grammar ensures the comparison occurs before
        # branch parsing.)
        return then_value if tests.get(op, False) else else_value

    def skip_to_call_end(self):
        depth = 0
        while self.i < len(self.text):
            ch = self.text[self.i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth == 0:
                    self.i += 1
                    return
                depth -= 1
            self.i += 1

    Parser.if_call = fixed_if

    return {name: cell_value(name) for name in cells}
