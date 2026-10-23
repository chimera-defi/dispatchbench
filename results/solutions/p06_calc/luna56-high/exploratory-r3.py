def calc(expr: str) -> int | str:
    n = len(expr)
    pos = 0

    def skip_spaces():
        nonlocal pos
        while pos < n and expr[pos] == " ":
            pos += 1

    def parse_primary():
        nonlocal pos
        skip_spaces()

        if expr[pos] == "(":
            pos += 1
            value = parse_add()
            skip_spaces()
            pos += 1  # ')'
            return value

        value = 0
        while pos < n and "0" <= expr[pos] <= "9":
            value = value * 10 + (ord(expr[pos]) - ord("0"))
            pos += 1
        return value

    def power_value(base: int, exponent: int) -> int:
        if exponent == 0:
            return 1
        if base == 0:
            return 0
        if base == 1:
            return 1
        if base == -1:
            return -1 if exponent & 1 else 1
        return base ** exponent

    def parse_power():
        nonlocal pos

        bases = [parse_primary()]
        negative_exponents = []

        while True:
            skip_spaces()
            if pos >= n or expr[pos] != "^":
                break

            pos += 1
            skip_spaces()

            negative = False
            while pos < n and expr[pos] == "-":
                negative = not negative
                pos += 1
                skip_spaces()

            bases.append(parse_primary())
            negative_exponents.append(negative)

        value = bases[-1]
        if value == "error":
            return "error"

        for i in range(len(negative_exponents) - 1, -1, -1):
            exponent = -value if negative_exponents[i] else value
            if exponent < 0:
                return "error"

            base = bases[i]
            if base == "error":
                return "error"

            value = power_value(base, exponent)

        return value

    def parse_unary():
        nonlocal pos

        negative = False
        skip_spaces()
        while pos < n and expr[pos] == "-":
            negative = not negative
            pos += 1
            skip_spaces()

        value = parse_power()
        if value == "error":
            return "error"
        return -value if negative else value

    def trunc_div(a: int, b: int) -> int:
        quotient = abs(a) // abs(b)
        return -quotient if (a < 0) != (b < 0) else quotient

    def parse_mul():
        nonlocal pos

        value = parse_unary()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "*/%":
                break

            operator = expr[pos]
            pos += 1
            right = parse_unary()

            if value == "error" or right == "error":
                value = "error"
                continue

            if operator == "*":
                value *= right
            elif operator == "/":
                if right == 0:
                    value = "error"
                else:
                    value = trunc_div(value, right)
            else:
                if right == 0:
                    value = "error"
                else:
                    value -= right * trunc_div(value, right)

        return value

    def parse_add():
        nonlocal pos

        value = parse_mul()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "+-":
                break

            operator = expr[pos]
            pos += 1
            right = parse_mul()

            if value == "error" or right == "error":
                value = "error"
            elif operator == "+":
                value += right
            else:
                value -= right

        return value

    return parse_add()
