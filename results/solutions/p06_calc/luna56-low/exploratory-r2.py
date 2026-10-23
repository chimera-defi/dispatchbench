def calc(expr: str) -> int | str:
    class EvalError(Exception):
        pass

    n = len(expr)
    pos = 0

    def skip_spaces():
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1

    def parse_primary():
        nonlocal pos
        skip_spaces()

        if pos < n and expr[pos] == '(':
            pos += 1
            value = parse_add()
            skip_spaces()
            pos += 1  # Input is guaranteed syntactically valid.
            return value

        start = pos
        while pos < n and expr[pos].isdigit():
            pos += 1
        return int(expr[start:pos])

    def parse_power():
        nonlocal pos

        bases = [parse_primary()]
        signs = []

        while True:
            skip_spaces()
            if pos >= n or expr[pos] != '^':
                break
            pos += 1

            skip_spaces()
            negative = False
            while pos < n and expr[pos] == '-':
                negative = not negative
                pos += 1
                skip_spaces()

            signs.append(negative)
            bases.append(parse_primary())

        value = bases[-1]
        for i in range(len(bases) - 2, -1, -1):
            exponent = value
            value = pow(bases[i], exponent) if exponent >= 0 else (_ for _ in ()).throw(EvalError())
            if signs[i]:
                value = -value

        return value

    def parse_unary():
        nonlocal pos
        negative = False
        skip_spaces()

        while pos < n and expr[pos] == '-':
            negative = not negative
            pos += 1
            skip_spaces()

        value = parse_power()
        return -value if negative else value

    def trunc_div(a, b):
        if b == 0:
            raise EvalError()
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def parse_mul():
        nonlocal pos
        value = parse_unary()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "*/%":
                return value

            op = expr[pos]
            pos += 1
            rhs = parse_unary()

            if op == '*':
                value *= rhs
            elif op == '/':
                value = trunc_div(value, rhs)
            else:
                value -= rhs * trunc_div(value, rhs)

    def parse_add():
        nonlocal pos
        value = parse_mul()

        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "+-":
                return value

            op = expr[pos]
            pos += 1
            rhs = parse_mul()
            value = value + rhs if op == '+' else value - rhs

    try:
        result = parse_add()
        skip_spaces()
        return result
    except EvalError:
        return "error"
