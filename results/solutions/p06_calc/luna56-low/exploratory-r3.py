def calc(expr: str) -> int | str:
    n = len(expr)
    i = 0

    def skip_spaces():
        nonlocal i
        while i < n and expr[i].isspace():
            i += 1

    def parse_atom():
        nonlocal i
        skip_spaces()

        if expr[i] == '(':
            i += 1
            value = parse_add()
            skip_spaces()
            i += 1  # ')'
            return value

        start = i
        while i < n and expr[i].isdigit():
            i += 1
        return int(expr[start:i])

    def parse_power():
        nonlocal i
        left = parse_atom()
        skip_spaces()

        if i < n and expr[i] == '^':
            i += 1
            right = parse_unary()
            if left is None or right is None or right < 0:
                return None
            return pow(left, right)

        return left

    def parse_unary():
        nonlocal i
        skip_spaces()

        negate = False
        while i < n and expr[i] == '-':
            negate = not negate
            i += 1
            skip_spaces()

        value = parse_power()
        if value is None:
            return None
        return -value if negate else value

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def parse_mul():
        nonlocal i
        value = parse_unary()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "*/%":
                break

            op = expr[i]
            i += 1
            right = parse_unary()

            if value is None or right is None:
                value = None
            elif right == 0:
                value = None
            elif op == '*':
                value *= right
            else:
                quotient = trunc_div(value, right)
                value = quotient if op == '/' else value - right * quotient

        return value

    def parse_add():
        nonlocal i
        value = parse_mul()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "+-":
                break

            op = expr[i]
            i += 1
            right = parse_mul()

            if value is None or right is None:
                value = None
            elif op == '+':
                value += right
            else:
                value -= right

        return value

    result = parse_add()
    return "error" if result is None else result
