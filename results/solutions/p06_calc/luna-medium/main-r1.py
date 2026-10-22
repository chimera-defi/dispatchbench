def calc(expr: str) -> int | str:
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        c = expr[i]
        if c == " ":
            i += 1
        elif c.isdigit():
            j = i + 1
            while j < n and expr[j].isdigit():
                j += 1
            tokens.append(int(expr[i:j]))
            i = j
        else:
            tokens.append(c)
            i += 1

    pos = 0

    def parse_primary():
        nonlocal pos
        token = tokens[pos]
        if token == "(":
            pos += 1
            value = parse_sum()
            pos += 1  # )
            return value
        pos += 1
        return token

    def parse_power():
        nonlocal pos
        base = parse_primary()
        if pos < len(tokens) and tokens[pos] == "^":
            pos += 1
            exponent = parse_unary()
            if exponent < 0:
                raise ZeroDivisionError
            base = pow(base, exponent)
        return base

    def parse_unary():
        nonlocal pos
        if pos < len(tokens) and tokens[pos] == "-":
            pos += 1
            return -parse_unary()
        return parse_power()

    def parse_product():
        nonlocal pos
        value = parse_unary()
        while pos < len(tokens) and tokens[pos] in ("*", "/", "%"):
            op = tokens[pos]
            pos += 1
            right = parse_unary()
            if op == "*":
                value *= right
            elif op == "/":
                if right == 0:
                    raise ZeroDivisionError
                quotient = abs(value) // abs(right)
                value = -quotient if (value < 0) != (right < 0) else quotient
            else:
                if right == 0:
                    raise ZeroDivisionError
                quotient = abs(value) // abs(right)
                if (value < 0) != (right < 0):
                    quotient = -quotient
                value -= right * quotient
        return value

    def parse_sum():
        nonlocal pos
        value = parse_product()
        while pos < len(tokens) and tokens[pos] in ("+", "-"):
            op = tokens[pos]
            pos += 1
            right = parse_product()
            value = value + right if op == "+" else value - right
        return value

    try:
        return parse_sum()
    except ZeroDivisionError:
        return "error"
