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

    tokens.append(None)
    pos = 0

    def parse_primary():
        nonlocal pos
        token = tokens[pos]
        if token == '(':
            pos += 1
            value = parse_sum()
            pos += 1  # closing parenthesis
            return value
        value = token
        pos += 1
        return value

    # Power is right-associative. Its left operand is a primary, while
    # its right operand can begin with unary minus.
    def parse_power():
        nonlocal pos
        base = parse_primary()
        if tokens[pos] == '^':
            pos += 1
            exponent = parse_unary()
            if exponent < 0:
                raise ArithmeticError
            base = pow(base, exponent)
        return base

    def parse_unary():
        nonlocal pos
        if tokens[pos] == '-':
            pos += 1
            return -parse_unary()
        return parse_power()

    def trunc_div(a, b):
        if b == 0:
            raise ArithmeticError
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def parse_product():
        nonlocal pos
        value = parse_unary()
        while tokens[pos] in ('*', '/', '%'):
            op = tokens[pos]
            pos += 1
            right = parse_unary()
            if op == '*':
                value *= right
            elif op == '/':
                value = trunc_div(value, right)
            else:
                value -= right * trunc_div(value, right)
        return value

    def parse_sum():
        nonlocal pos
        value = parse_product()
        while tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            right = parse_product()
            value = value + right if op == '+' else value - right
        return value

    try:
        return parse_sum()
    except ArithmeticError:
        return "error"
