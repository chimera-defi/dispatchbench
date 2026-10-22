def calc(expr: str) -> int | str:
    class _Error(Exception):
        pass

    s = "".join(expr.split())
    n = len(s)
    pos = 0

    def peek():
        return s[pos] if pos < n else ""

    def parse_number():
        nonlocal pos
        start = pos
        while pos < n and s[pos] in "0123456789":
            pos += 1
        digits = s[start:pos]
        # Build the value in chunks so int() never hits the digit-count limit.
        v = 0
        for i in range(0, len(digits), 1000):
            chunk = digits[i:i + 1000]
            v = v * (10 ** len(chunk)) + int(chunk)
        return v

    def parse_primary():
        nonlocal pos
        if peek() == "(":
            pos += 1
            v = parse_expr()
            pos += 1  # consume ')'
            return v
        return parse_number()

    def parse_power():
        nonlocal pos
        # Flatten the right-associative chain: p0 ^ [-]* p1 ^ [-]* p2 ...
        bases = [parse_primary()]
        signs = []
        while peek() == "^":
            pos += 1
            negs = 0
            while peek() == "-":
                negs += 1
                pos += 1
            signs.append(negs % 2 == 1)
            bases.append(parse_primary())
        # Evaluate from the right: the exponent is the (possibly negated) tower to the right.
        v = bases[-1]
        for i in range(len(bases) - 2, -1, -1):
            e = -v if signs[i] else v
            if e < 0:
                raise _Error()
            v = bases[i] ** e
        return v

    def parse_unary():
        nonlocal pos
        neg = False
        while peek() == "-":
            neg = not neg
            pos += 1
        v = parse_power()
        return -v if neg else v

    def parse_term():
        nonlocal pos
        v = parse_unary()
        while peek() in ("*", "/", "%"):
            op = s[pos]
            pos += 1
            r = parse_unary()
            if op == "*":
                v *= r
                continue
            if r == 0:
                raise _Error()
            # Truncate toward zero.
            q = abs(v) // abs(r)
            if (v < 0) != (r < 0):
                q = -q
            v = q if op == "/" else v - r * q
        return v

    def parse_expr():
        nonlocal pos
        v = parse_term()
        while peek() in ("+", "-"):
            op = s[pos]
            pos += 1
            r = parse_term()
            v = v + r if op == "+" else v - r
        return v

    try:
        return parse_expr()
    except _Error:
        return "error"
