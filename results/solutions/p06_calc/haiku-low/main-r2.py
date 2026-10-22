def calc(expr: str) -> int | str:
    s = expr.replace(" ", "")
    n = len(s)
    pos = 0

    class Err(Exception):
        pass

    def tdiv(a, b):
        if b == 0:
            raise Err()
        q = abs(a) // abs(b)
        return q if (a >= 0) == (b >= 0) else -q

    def peek():
        return s[pos] if pos < n else ""

    def parse_expr():
        nonlocal pos
        v = parse_term()
        while peek() in ("+", "-"):
            op = s[pos]
            pos += 1
            r = parse_term()
            v = v + r if op == "+" else v - r
        return v

    def parse_term():
        nonlocal pos
        v = parse_unary()
        while peek() in ("*", "/", "%"):
            op = s[pos]
            pos += 1
            r = parse_unary()
            if op == "*":
                v = v * r
            elif op == "/":
                v = tdiv(v, r)
            else:
                v = v - r * tdiv(v, r)
        return v

    def parse_unary():
        nonlocal pos
        if peek() == "-":
            pos += 1
            return -parse_unary()
        return parse_power()

    def parse_power():
        nonlocal pos
        base = parse_atom()
        if peek() == "^":
            pos += 1
            exp = parse_unary()  # right operand may start with unary minus
            if exp < 0:
                raise Err()
            if base == 0 and exp == 0:
                return 1
            return base ** exp
        return base

    def parse_atom():
        nonlocal pos
        if peek() == "(":
            pos += 1
            v = parse_expr()
            if peek() != ")":
                raise Err()
            pos += 1
            return v
        start = pos
        while pos < n and s[pos].isdigit():
            pos += 1
        if start == pos:
            raise Err()
        return int(s[start:pos])

    try:
        result = parse_expr()
        if pos != n:
            return "error"
        return result
    except Err:
        return "error"
