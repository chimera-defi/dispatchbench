import sys


class _CalcError(Exception):
    pass


def calc(expr: str) -> int | str:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)

    s = "".join(expr.split())
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        if c.isdigit():
            j = i
            while j < len(s) and s[j].isdigit():
                j += 1
            tokens.append(int(s[i:j]))
            i = j
        else:
            tokens.append(c)
            i += 1

    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def parse_expr():
        nonlocal pos
        v = parse_term()
        while peek() in ("+", "-"):
            op = tokens[pos]
            pos += 1
            r = parse_term()
            v = v + r if op == "+" else v - r
        return v

    def parse_term():
        nonlocal pos
        v = parse_unary()
        while peek() in ("*", "/", "%"):
            op = tokens[pos]
            pos += 1
            r = parse_unary()
            if op == "*":
                v = v * r
            else:
                if r == 0:
                    raise _CalcError()
                q = abs(v) // abs(r)
                if (v < 0) != (r < 0):
                    q = -q
                v = q if op == "/" else v - r * q
        return v

    def parse_unary():
        nonlocal pos
        neg = False
        while peek() == "-":
            neg = not neg
            pos += 1
        v = parse_power()
        return -v if neg else v

    def parse_power():
        nonlocal pos
        base = parse_primary()
        if peek() == "^":
            pos += 1
            exp = parse_unary()
            if exp < 0:
                raise _CalcError()
            return base ** exp
        return base

    def parse_primary():
        nonlocal pos
        t = tokens[pos]
        pos += 1
        if t == "(":
            v = parse_expr()
            pos += 1  # consume ')'
            return v
        return t

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 20000))
    try:
        return parse_expr()
    except _CalcError:
        return "error"
    finally:
        sys.setrecursionlimit(old_limit)
