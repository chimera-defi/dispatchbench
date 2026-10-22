def calc(expr: str) -> int | str:
    error = object()
    i = 0
    n = len(expr)

    def skip_spaces():
        nonlocal i
        while i < n and expr[i] == " ":
            i += 1

    def parse_primary():
        nonlocal i
        skip_spaces()

        if expr[i] == "(":
            i += 1
            value = parse_add()
            skip_spaces()
            i += 1  # ")"
            return value

        start = i
        while i < n and "0" <= expr[i] <= "9":
            i += 1
        return int(expr[start:i])

    def parse_power():
        nonlocal i
        value = parse_primary()
        skip_spaces()

        if i < n and expr[i] == "^":
            i += 1
            exponent = parse_unary()
            if value is error or exponent is error or exponent < 0:
                return error
            return value ** exponent

        return value

    def parse_unary():
        nonlocal i
        skip_spaces()
        if i < n and expr[i] == "-":
            i += 1
            value = parse_unary()
            return error if value is error else -value
        return parse_power()

    def parse_mul():
        nonlocal i
        value = parse_unary()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "*/%":
                return value

            op = expr[i]
            i += 1
            right = parse_unary()

            if value is error or right is error:
                value = error
            elif op == "*":
                value *= right
            elif right == 0:
                value = error
            else:
                quotient = abs(value) // abs(right)
                if (value < 0) != (right < 0):
                    quotient = -quotient
                value = quotient if op == "/" else value - right * quotient

    def parse_add():
        nonlocal i
        value = parse_mul()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "+-":
                return value

            op = expr[i]
            i += 1
            right = parse_mul()

            if value is error or right is error:
                value = error
            elif op == "+":
                value += right
            else:
                value -= right

    result = parse_add()
    return "error" if result is error else result
