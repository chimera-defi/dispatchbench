def calc(expr: str) -> int | str:
    class ParseError(Exception):
        pass

    class Parser:
        def __init__(self, text: str):
            self.text = text
            self.i = 0
            self.n = len(text)

        def skip_spaces(self):
            while self.i < self.n and self.text[self.i] == " ":
                self.i += 1

        def take(self, char: str) -> bool:
            self.skip_spaces()
            if self.i < self.n and self.text[self.i] == char:
                self.i += 1
                return True
            return False

        def parse_primary(self) -> int:
            self.skip_spaces()
            if self.i < self.n and self.text[self.i] == "(":
                self.i += 1
                value = self.parse_expression()
                if not self.take(")"):
                    raise ParseError
                return value

            if self.i >= self.n or not self.text[self.i].isdigit():
                raise ParseError

            value = 0
            while self.i < self.n and self.text[self.i].isdigit():
                value = value * 10 + ord(self.text[self.i]) - ord("0")
                self.i += 1
            return value

        def parse_unary(self) -> int:
            sign = 1
            while self.take("-"):
                sign = -sign
            return sign * self.parse_power()

        def parse_power(self) -> int:
            bases = [self.parse_primary()]
            signs = [1]

            while self.take("^"):
                sign = 1
                while self.take("-"):
                    sign = -sign
                signs.append(sign)
                bases.append(self.parse_primary())

            value = bases[-1]
            for i in range(len(bases) - 2, -1, -1):
                exponent = signs[i + 1] * value
                if exponent < 0:
                    raise ParseError
                value = pow(bases[i], exponent)
            return value

        def parse_term(self) -> int:
            value = self.parse_unary()
            while True:
                if self.take("*"):
                    value *= self.parse_unary()
                elif self.take("/"):
                    divisor = self.parse_unary()
                    if divisor == 0:
                        raise ParseError
                    quotient = abs(value) // abs(divisor)
                    value = -quotient if (value < 0) != (divisor < 0) else quotient
                elif self.take("%"):
                    divisor = self.parse_unary()
                    if divisor == 0:
                        raise ParseError
                    quotient = abs(value) // abs(divisor)
                    if (value < 0) != (divisor < 0):
                        quotient = -quotient
                    value -= divisor * quotient
                else:
                    return value

        def parse_expression(self) -> int:
            value = self.parse_term()
            while True:
                if self.take("+"):
                    value += self.parse_term()
                elif self.take("-"):
                    value -= self.parse_term()
                else:
                    return value

    try:
        parser = Parser(expr)
        result = parser.parse_expression()
        parser.skip_spaces()
        if parser.i != parser.n:
            return "error"
        return result
    except (ParseError, RecursionError):
        return "error"
