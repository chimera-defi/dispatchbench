def calc(expr: str) -> int | str:
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        c = expr[i]
        if c.isspace():
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

    def parse_sum():
        nonlocal pos
        value = parse_product()
        while pos < len(tokens) and tokens[pos] in ("+", "-"):
            op = tokens[pos]
            pos += 1
            rhs = parse_product()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_product():
        nonlocal pos
        value = parse_unary()
        while pos < len(tokens) and tokens[pos] in ("*", "/", "%"):
            op = tokens[pos]
            pos += 1
            rhs = parse_unary()
            if op == "*":
                value *= rhs
            elif op == "/":
                if rhs == 0:
                    raise ZeroDivisionError
                q = abs(value) // abs(rhs)
                value = -q if (value < 0) != (rhs < 0) else q
            else:
                if rhs == 0:
                    raise ZeroDivisionError
                q = abs(value) // abs(rhs)
                q = -q if (value < 0) != (rhs < 0) else q
                value -= rhs * q
        return value

    def parse_unary():
        nonlocal pos
        if pos < len(tokens) and tokens[pos] == "-":
            pos += 1
            return -parse_unary()
        return parse_power()

    def parse_power():
        nonlocal pos
        value = parse_atom()
        if pos < len(tokens) and tokens[pos] == "^":
            pos += 1
            exponent = parse_unary()
            if exponent < 0:
                raise ValueError
            value = value ** exponent
        return value

    def parse_atom():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token == "(":
            value = parse_sum()
            pos += 1  # closing parenthesis
            return value
        return token

    try:
        return parse_sum()
    except (ZeroDivisionError, ValueError):
        return "error"
