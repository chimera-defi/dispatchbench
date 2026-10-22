class _CalcError(Exception):
    pass


class _Parser:
    def __init__(self, expr: str):
        self.expr = expr
        self.i = 0
        self.n = len(expr)

    def skip_spaces(self):
        while self.i < self.n and self.expr[self.i] == " ":
            self.i += 1

    def parse_expression(self):
        value = self.parse_product()
        while True:
            self.skip_spaces()
            if self.i >= self.n or self.expr[self.i] not in "+-":
                return value
            op = self.expr[self.i]
            self.i += 1
            rhs = self.parse_product()
            value = value + rhs if op == "+" else value - rhs

    def parse_product(self):
        value = self.parse_unary()
        while True:
            self.skip_spaces()
            if self.i >= self.n or self.expr[self.i] not in "*/%":
                return value
            op = self.expr[self.i]
            self.i += 1
            rhs = self.parse_unary()
            if op in "/%":
                if rhs == 0:
                    raise _CalcError
                quotient = abs(value) // abs(rhs)
                if (value < 0) != (rhs < 0):
                    quotient = -quotient
                value = quotient if op == "/" else value - rhs * quotient
            else:
                value *= rhs

    def parse_unary(self):
        self.skip_spaces()
        negative = False
        while self.i < self.n and self.expr[self.i] == "-":
            negative = not negative
            self.i += 1
            self.skip_spaces()
        value = self.parse_power()
        return -value if negative else value

    def parse_power(self):
        bases = [self.parse_atom()]
        signs = []

        while True:
            self.skip_spaces()
            if self.i >= self.n or self.expr[self.i] != "^":
                break
            self.i += 1
            self.skip_spaces()

            negative = False
            while self.i < self.n and self.expr[self.i] == "-":
                negative = not negative
                self.i += 1
                self.skip_spaces()

            signs.append(negative)
            bases.append(self.parse_atom())

        value = bases[-1]
        for i in range(len(signs) - 1, -1, -1):
            exponent = -value if signs[i] else value
            if exponent < 0:
                raise _CalcError
            value = pow(bases[i], exponent)
        return value

    def parse_atom(self):
        self.skip_spaces()
        if self.expr[self.i] == "(":
            self.i += 1
            value = self.parse_expression()
            self.skip_spaces()
            self.i += 1  # closing parenthesis
            return value

        value = 0
        while self.i < self.n and "0" <= self.expr[self.i] <= "9":
            value = value * 10 + ord(self.expr[self.i]) - ord("0")
            self.i += 1
        return value


def calc(expr: str) -> int | str:
    try:
        return _Parser(expr).parse_expression()
    except _CalcError:
        return "error"
