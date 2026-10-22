import re

ERRORS = {"#DIV/0!", "#CYCLE!"}


class Parser:
    def __init__(self, text, get_cell, defined):
        self.text = text
        self.pos = 0
        self.get_cell = get_cell
        self.defined = defined

    def spaces(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def peek(self, token):
        self.spaces()
        return self.text.startswith(token, self.pos)

    def take(self, token):
        if not self.peek(token):
            raise ValueError("invalid formula")
        self.pos += len(token)

    def identifier(self):
        self.spaces()
        match = re.match(r"[A-Z][1-9][0-9]?", self.text[self.pos:])
        if not match:
            raise ValueError("invalid identifier")
        name = match.group()
        self.pos += len(name)
        return name

    def formula(self):
        return self.additive()

    def additive(self):
        value = self.multiplicative()
        while True:
            if self.peek("+"):
                self.take("+")
                if value in ERRORS:
                    return value
                right = self.multiplicative()
                if right in ERRORS:
                    return right
                value += right
            elif self.peek("-"):
                self.take("-")
                if value in ERRORS:
                    return value
                right = self.multiplicative()
                if right in ERRORS:
                    return right
                value -= right
            else:
                return value

    def multiplicative(self):
        value = self.unary()
        while True:
            if self.peek("*"):
                self.take("*")
                if value in ERRORS:
                    return value
                right = self.unary()
                if right in ERRORS:
                    return right
                value *= right
            elif self.peek("/"):
                self.take("/")
                if value in ERRORS:
                    return value
                right = self.unary()
                if right in ERRORS:
                    return right
                if right == 0:
                    return "#DIV/0!"
                quotient = abs(value) // abs(right)
                value = -quotient if (value < 0) != (right < 0) else quotient
            else:
                return value

    def unary(self):
        if self.peek("-"):
            self.take("-")
            value = self.unary()
            return value if value in ERRORS else -value
        return self.atom()

    def atom(self):
        self.spaces()
        if self.peek("("):
            self.take("(")
            value = self.formula()
            self.take(")")
            return value

        if self.pos < len(self.text) and self.text[self.pos].isdigit():
            match = re.match(r"\d+", self.text[self.pos:])
            self.pos += len(match.group())
            return int(match.group())

        self.spaces()
        if self.pos < len(self.text) and self.text[self.pos].isupper():
            name = self.identifier()
            if self.peek("("):
                return self.function(name)
            return self.get_cell(name)

        raise ValueError("invalid atom")

    def function(self, name):
        self.take("(")
        if name == "IF":
            left = self.formula()
            self.take(",")
            right = self.formula()
            if left in ERRORS:
                self.take(",")
                self.formula()
                self.take(",")
                self.formula()
                self.take(")")
                return left
            if right in ERRORS:
                self.take(",")
                self.formula()
                self.take(",")
                self.formula()
                self.take(")")
                return right

            self.spaces()
            op = next((op for op in ("<>", "<=", ">=", "=", "<", ">")
                       if self.text.startswith(op, self.pos)), None)
            if op is None:
                raise ValueError("invalid comparison")
            self.pos += len(op)

            # IF grammar places the comparison operator between left and right.
            # Parsing left as a formula above stops before the comparison.
            # (The right operand was parsed after the comma only for ordinary
            # functions; recover the intended syntax below.)
            raise ValueError("invalid IF")

        if name not in ("SUM", "MIN", "MAX"):
            raise ValueError("invalid function")

        values = []
        while True:
            self.spaces()
            start = self.pos
            match = re.match(r"[A-Z][1-9][0-9]?\s*:\s*[A-Z][1-9][0-9]?", self.text[self.pos:])
            if match:
                self.pos += len(match.group())
                a, b = re.findall(r"[A-Z][1-9][0-9]?", match.group())
                c1, r1 = ord(a[0]) - 65, int(a[1:])
                c2, r2 = ord(b[0]) - 65, int(b[1:])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell = chr(65 + col) + str(row)
                        if cell in self.defined:
                            value = self.get_cell(cell)
                            if value in ERRORS:
                                return value
                            values.append(value)
            else:
                value = self.formula()
                if value in ERRORS:
                    return value
                values.append(value)

            if self.peek(","):
                self.take(",")
            else:
                break

        self.take(")")
        if name == "SUM":
            return sum(values)
        if not values:
            return 0
        return min(values) if name == "MIN" else max(values)


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    values = {}
    active = set()

    def get_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return "#CYCLE!"
        active.add(name)
        content = cells[name]
        if content.startswith("="):
            parser = Parser(content[1:], get_cell, cells)
            value = parser.formula()
        else:
            value = int(content)
        active.remove(name)
        values[name] = value
        return value

    return {name: get_cell(name) for name in cells}
