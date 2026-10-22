def calc(expr: str) -> int | str:
    s = expr
    n = len(s)
    i = 0

    def skip_spaces():
        nonlocal i
        while i < n and s[i] == " ":
            i += 1

    def parse_primary():
        nonlocal i
        skip_spaces()
        if s[i] == "(":
            i += 1
            value = parse_add()
            skip_spaces()
            i += 1  # closing parenthesis
            return value

        start = i
        while i < n and s[i].isdigit():
            i += 1
        return int(s[start:i])

    # Power binds tighter than unary minus, while allowing a signed exponent.
    def parse_power():
        nonlocal i
        value = parse_primary()
        skip_spaces()
        if i < n and s[i] == "^":
            i += 1
            exponent = parse_unary()
            if exponent < 0:
                raise ValueError
            value = value ** exponent
        return value

    def parse_unary():
        nonlocal i
        skip_spaces()
        if i < n and s[i] == "-":
            i += 1
            return -parse_unary()
        return parse_power()

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def parse_mul():
        nonlocal i
        value = parse_unary()
        while True:
            skip_spaces()
            if i < n and s[i] in "*/%":
                op = s[i]
                i += 1
                rhs = parse_unary()
                if op == "*":
                    value *= rhs
                else:
                    if rhs == 0:
                        raise ValueError
                    q = trunc_div(value, rhs)
                    value = q if op == "/" else value - rhs * q
            else:
                return value

    def parse_add():
        nonlocal i
        value = parse_mul()
        while True:
            skip_spaces()
            if i < n and s[i] in "+-":
                op = s[i]
                i += 1
                rhs = parse_mul()
                value = value + rhs if op == "+" else value - rhs
            else:
                return value

    try:
        result = parse_add()
        return result
    except (ValueError, ZeroDivisionError):
        return "error"
