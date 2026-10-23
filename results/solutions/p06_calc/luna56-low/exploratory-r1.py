def calc(expr: str) -> int | str:
    import sys

    n = len(expr)
    i = 0
    ERR = object()

    old_limit = sys.getrecursionlimit()
    if old_limit < 2 * n + 100:
        sys.setrecursionlimit(2 * n + 100)

    def skip_spaces():
        nonlocal i
        while i < n and expr[i].isspace():
            i += 1

    def parse_primary():
        nonlocal i
        skip_spaces()

        if expr[i] == '(':
            i += 1
            value = parse_additive()
            skip_spaces()
            i += 1  # ')'
            return value

        value = 0
        while i < n and '0' <= expr[i] <= '9':
            value = value * 10 + (ord(expr[i]) - ord('0'))
            i += 1
        return value

    def parse_power():
        nonlocal i
        left = parse_primary()
        skip_spaces()

        if i < n and expr[i] == '^':
            i += 1
            right = parse_unary()
            if left is ERR or right is ERR or right < 0:
                return ERR
            return left ** right

        return left

    def parse_unary():
        nonlocal i
        negate = False
        skip_spaces()

        while i < n and expr[i] == '-':
            negate = not negate
            i += 1
            skip_spaces()

        value = parse_power()
        if value is ERR:
            return ERR
        return -value if negate else value

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def parse_multiplicative():
        nonlocal i
        value = parse_unary()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "*/%":
                return value

            op = expr[i]
            i += 1
            right = parse_unary()

            if value is ERR or right is ERR:
                value = ERR
            elif right == 0 and op in "/%":
                value = ERR
            elif op == '*':
                value *= right
            elif op == '/':
                value = trunc_div(value, right)
            else:
                q = trunc_div(value, right)
                value = value - right * q

    def parse_additive():
        nonlocal i
        value = parse_multiplicative()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "+-":
                return value

            op = expr[i]
            i += 1
            right = parse_multiplicative()

            if value is ERR or right is ERR:
                value = ERR
            elif op == '+':
                value += right
            else:
                value -= right

    result = parse_additive()

    if sys.getrecursionlimit() != old_limit:
        sys.setrecursionlimit(old_limit)

    return "error" if result is ERR else result
