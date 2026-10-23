def calc(expr: str) -> int | str:
    n = len(expr)
    pos = 0
    ERROR = "error"

    def skip_spaces() -> None:
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1

    def parse_primary() -> int | str:
        nonlocal pos
        skip_spaces()

        if expr[pos] == "(":
            pos += 1
            value = parse_additive()
            skip_spaces()
            pos += 1  # ')'
            return value

        start = pos
        while pos < n and expr[pos].isdigit():
            pos += 1
        return int(expr[start:pos])

    def parse_power() -> int | str:
        nonlocal pos
        base = parse_primary()
        skip_spaces()

        if pos < n and expr[pos] == "^":
            pos += 1
            exponent = parse_unary()
            if base == ERROR or exponent == ERROR:
                return ERROR
            if exponent < 0:
                return ERROR
            return base ** exponent

        return base

    def parse_unary() -> int | str:
        nonlocal pos
        skip_spaces()

        if pos < n and expr[pos] == "-":
            pos += 1
            value = parse_unary()
            return ERROR if value == ERROR else -value

        return parse_power()

    def trunc_div(a: int, b: int) -> int:
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def parse_multiplicative() -> int | str:
        nonlocal pos
        value = parse_unary()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "*/%":
                return value

            op = expr[pos]
            pos += 1
            rhs = parse_unary()

            if value == ERROR or rhs == ERROR:
                value = ERROR
            elif rhs == 0:
                value = ERROR
            elif op == "*":
                value *= rhs
            else:
                quotient = trunc_div(value, rhs)
                value = quotient if op == "/" else value - rhs * quotient

    def parse_additive() -> int | str:
        nonlocal pos
        value = parse_multiplicative()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "+-":
                return value

            op = expr[pos]
            pos += 1
            rhs = parse_multiplicative()

            if value == ERROR or rhs == ERROR:
                value = ERROR
            elif op == "+":
                value += rhs
            else:
                value -= rhs

    return parse_additive()
