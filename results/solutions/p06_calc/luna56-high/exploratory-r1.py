def calc(expr: str) -> int | str:
    n = len(expr)
    i = 0
    bad = False

    def skip_spaces():
        nonlocal i
        while i < n and expr[i] == " ":
            i += 1

    def parse_atom():
        nonlocal i
        skip_spaces()

        if expr[i] == "(":
            i += 1
            value = parse_add()
            skip_spaces()
            i += 1  # ')'
            return value

        value = 0
        while i < n and "0" <= expr[i] <= "9":
            value = value * 10 + (ord(expr[i]) - ord("0"))
            i += 1
        return value

    def parse_power():
        nonlocal i, bad

        bases = [parse_atom()]
        signs = []

        while True:
            skip_spaces()
            if i >= n or expr[i] != "^":
                break

            i += 1
            skip_spaces()

            negative = False
            while i < n and expr[i] == "-":
                negative = not negative
                i += 1
                skip_spaces()

            bases.append(parse_atom())
            signs.append(-1 if negative else 1)

        if bad:
            return 0

        value = bases[-1]
        for j in range(len(signs) - 1, -1, -1):
            exponent = signs[j] * value
            if exponent < 0:
                bad = True
                return 0
            value = pow(bases[j], exponent)

        return value

    def parse_unary():
        nonlocal i
        skip_spaces()

        negative = False
        while i < n and expr[i] == "-":
            negative = not negative
            i += 1
            skip_spaces()

        value = parse_power()
        return -value if negative else value

    def parse_mul():
        nonlocal i, bad
        value = parse_unary()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "*/%":
                break

            op = expr[i]
            i += 1
            right = parse_unary()

            if bad:
                value = 0
                continue

            if op == "*":
                value *= right
            elif right == 0:
                bad = True
                value = 0
            elif op == "/":
                quotient = abs(value) // abs(right)
                if (value < 0) != (right < 0):
                    quotient = -quotient
                value = quotient
            else:
                quotient = abs(value) // abs(right)
                if (value < 0) != (right < 0):
                    quotient = -quotient
                value = value - right * quotient

        return value

    def parse_add():
        nonlocal i, bad
        value = parse_mul()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "+-":
                break

            op = expr[i]
            i += 1
            right = parse_mul()

            if bad:
                value = 0
            elif op == "+":
                value += right
            else:
                value -= right

        return value

    result = parse_add()
    return "error" if bad else result
