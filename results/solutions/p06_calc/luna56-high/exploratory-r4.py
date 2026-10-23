def calc(expr: str) -> int | str:
    ERROR = object()
    n = len(expr)
    pos = 0

    def skip_spaces():
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1

    def parse_primary():
        nonlocal pos
        skip_spaces()

        if pos < n and expr[pos] == "(":
            pos += 1
            value = parse_add()
            skip_spaces()
            pos += 1
            return value

        value = 0
        while pos < n and "0" <= expr[pos] <= "9":
            value = value * 10 + ord(expr[pos]) - ord("0")
            pos += 1
        return value

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        if (a < 0) != (b < 0):
            q = -q
        return q

    def parse_unary_power():
        nonlocal pos

        skip_spaces()
        leading_minus = 0
        while pos < n and expr[pos] == "-":
            leading_minus ^= 1
            pos += 1
            skip_spaces()

        values = [parse_primary()]
        minus_flags = [leading_minus]

        while True:
            skip_spaces()
            if pos >= n or expr[pos] != "^":
                break

            pos += 1
            skip_spaces()

            minus = 0
            while pos < n and expr[pos] == "-":
                minus ^= 1
                pos += 1
                skip_spaces()

            value = parse_primary()
            if value is ERROR:
                return ERROR

            values.append(value)
            minus_flags.append(minus)

        result = values[-1]

        for i in range(len(values) - 2, -1, -1):
            exponent = -result if minus_flags[i + 1] else result
            if exponent < 0:
                return ERROR
            result = pow(values[i], exponent)

        if minus_flags[0]:
            result = -result

        return result

    def parse_mul():
        nonlocal pos
        value = parse_unary_power()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "*/%":
                break

            operator = expr[pos]
            pos += 1
            right = parse_unary_power()

            if value is ERROR or right is ERROR:
                return ERROR

            if operator == "*":
                value *= right
            elif right == 0:
                return ERROR
            elif operator == "/":
                value = trunc_div(value, right)
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

            if value is ERROR or right is ERROR:
                return ERROR

            if operator == "+":
                value += right
            else:
                value -= right

        return value

    result = parse_add()
    return "error" if result is ERROR else result
