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

    def parse_primary():
        nonlocal pos
        token = tokens[pos]
        if token == "(":
            pos += 1
            value = parse_add()
            pos += 1  # closing parenthesis
            return value
        pos += 1
        return token

    # Power binds tighter than unary minus, while its right operand
    # is allowed to begin with unary minus.
    def parse_power():
        nonlocal pos
        value = parse_primary()
        if pos < len(tokens) and tokens[pos] == "^":
            pos += 1
            exponent = parse_unary()
            if exponent < 0:
                raise ArithmeticError
            value = value ** exponent
        return value

    def parse_unary():
        nonlocal pos
        if pos < len(tokens) and tokens[pos] == "-":
            pos += 1
            return -parse_unary()
        return parse_power()

    def trunc_div(a, b):
        quotient = abs(a) // abs(b)
        return -quotient if (a < 0) != (b < 0) else quotient

    def parse_mul():
        nonlocal pos
        value = parse_unary()
        while pos < len(tokens) and tokens[pos] in ("*", "/", "%"):
            op = tokens[pos]
            pos += 1
            right = parse_unary()
            if op == "*":
                value *= right
            elif right == 0:
                raise ArithmeticError
            elif op == "/":
                value = trunc_div(value, right)
            else:
                value -= right * trunc_div(value, right)
        return value

    def parse_add():
        nonlocal pos
        value = parse_mul()
        while pos < len(tokens) and tokens[pos] in ("+", "-"):
            op = tokens[pos]
            pos += 1
            right = parse_mul()
            value = value + right if op == "+" else value - right
        return value

    try:
        return parse_add()
    except ArithmeticError:
        return "error"
