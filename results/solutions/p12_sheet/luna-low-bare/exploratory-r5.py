def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    cache = {}
    active = set()

    def col_row(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def cell_value(name):
        if name not in cells:
            return 0
        if name in cache:
            return cache[name]
        if name in active:
            return CYCLE

        active.add(name)
        content = cells[name].strip()
        if content.lstrip("-").isdigit():
            value = int(content)
        else:
            parser = Parser(content[1:], cell_value, cells, DIV0, CYCLE)
            value = parser.parse()
        active.remove(name)
        cache[name] = value
        return value

    class Parser:
        def __init__(self, text, reference, cells, div0, cycle):
            self.text = text
            self.i = 0
            self.reference = reference
            self.cells = cells
            self.div0 = div0
            self.cycle = cycle

        def skip(self):
            while self.i < len(self.text) and self.text[self.i].isspace():
                self.i += 1

        def peek(self):
            self.skip()
            return self.text[self.i] if self.i < len(self.text) else ""

        def take(self, token):
            self.skip()
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
                    return self.div0
                else:
                    quotient = abs(value) // abs(right)
                    value = -quotient if (value < 0) != (right < 0) else quotient

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

            ch = self.peek()
            if ch.isdigit():
                start = self.i
                while self.i < len(self.text) and self.text[self.i].isdigit():
                    self.i += 1
                return int(self.text[start:self.i])

            if ch.isalpha():
                start = self.i
                while self.i < len(self.text) and self.text[self.i].isalpha():
                    self.i += 1
                name = self.text[start:self.i].upper()
                if self.take("("):
                    if name == "IF":
                        left = self.expr()
                        op = self.comparison_operator()
                        right = self.expr()
                        self.take(",")
                        if isinstance(left, str):
                            self.expr()
                            self.take(",")
                            self.expr()
                            self.take(")")
                            return left
                        if isinstance(right, str):
                            self.expr()
                            self.take(",")
                            self.expr()
                            self.take(")")
                            return right
                        condition = {
                            "=": left == right, "<>": left != right,
                            "<": left < right, "<=": left <= right,
                            ">": left > right, ">=": left >= right,
                        }[op]
                        self.take(",")
                        chosen = self.expr() if condition else None
                        self.take(",")
                        other = self.expr()
                        self.take(")")
                        return chosen if condition else other

                    values = []
                    while True:
                        self.skip()
                        saved = self.i
                        first = self.read_cell_name()
                        if first is not None and self.take(":"):
                            second = self.read_cell_name()
                            c1, r1 = col_row(first)
                            c2, r2 = col_row(second)
                            for row in range(min(r1, r2), max(r1, r2) + 1):
                                for col in range(min(c1, c2), max(c1, c2) + 1):
                                    cell = chr(ord("A") + col) + str(row)
                                    if cell in self.cells:
                                        values.append(self.reference(cell))
                                        if isinstance(values[-1], str):
                                            self.consume_function_tail()
                                            return values[-1]
                        else:
                            self.i = saved
                            value = self.expr()
                            values.append(value)
                            if isinstance(value, str):
                                self.consume_function_tail()
                                return value
                        if self.take(")"):
                            break
                        self.take(",")

                    if not values:
                        return 0
                    nums = values
                    if name == "SUM":
                        return sum(nums)
                    if name == "MIN":
                        return min(nums)
                    return max(nums)

                self.i = start
                cell = self.read_cell_name()
                return self.reference(cell)

            return 0

        def comparison_operator(self):
            for op in ("<=", ">=", "<>", "=", "<", ">"):
                if self.take(op):
                    return op
            return "="

        def read_cell_name(self):
            self.skip()
            start = self.i
            if self.i < len(self.text) and "A" <= self.text[self.i].upper() <= "Z":
                self.i += 1
                while self.i < len(self.text) and self.text[self.i].isdigit():
                    self.i += 1
                if self.i > start + 1:
                    return self.text[start:self.i].upper()
            self.i = start
            return None

        def consume_function_tail(self):
            depth = 0
            while self.i < len(self.text):
                ch = self.text[self.i]
                self.i += 1
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    if depth == 0:
                        return
                    depth -= 1

    return {name: cell_value(name) for name in cells}
