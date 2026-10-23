def calc(expr: str) -> int | str:
    class EvalError(Exception):
        pass

    n = len(expr)
    pos = 0

    def skip_spaces():
        nonlocal pos
        while pos < n and expr[pos] == " ":
            pos += 1

    def take(ch: str) -> bool:
        nonlocal pos
        skip_spaces()
        if pos < n and expr[pos] == ch:
            pos += 1
            return True
        return False

    def parse_number() -> int:
        nonlocal pos
        skip_spaces()
        value = 0
        while pos < n and "0" <= expr[pos] <= "9":
            value = value * 10 + (ord(expr[pos]) - ord("0"))
            pos += 1
        return value

    def trunc_div(a: int, b: int) -> int:
        if b == 0:
            raise EvalError
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def int_pow(a: int, b: int) -> int:
        if b < 0:
            raise EvalError
        return pow(a, b)

    def parse_primary() -> int:
        if take("("):
            value = parse_additive()
            take(")")
            return value
        return parse_number()

    def parse_power() -> int:
        values = [parse_primary()]
        signs = []

        while take("^"):
            negative = False
            while take("-"):
                negative = not negative
            values.append(parse_primary())
            signs.append(negative)

        if len(values) == 1:
            return values[0]

        value = -values[-1] if signs[-1] else values[-1]

        for j in range(len(values) - 2, 0, -1):
            value = int_pow(values[j], value)
            if signs[j - 1]:
                value = -value

        return int_pow(values[0], value)

    def parse_unary() -> int:
        negative = False
        while take("-"):
            negative = not negative
        value = parse_power()
        return -value if negative else value

    def parse_multiplicative() -> int:
        value = parse_unary()

        while True:
            if take("*"):
                value *= parse_unary()
            elif take("/"):
                value = trunc_div(value, parse_unary())
            elif take("%"):
                divisor = parse_unary()
                quotient = trunc_div(value, divisor)
                value -= divisor * quotient
            else:
                return value

    def parse_additive() -> int:
        value = parse_multiplicative()

        while True:
            if take("+"):
                value += parse_multiplicative()
            elif take("-"):
                value -= parse_multiplicative()
            else:
                return value

    try:
        return parse_additive()
    except EvalError:
        return "error"
