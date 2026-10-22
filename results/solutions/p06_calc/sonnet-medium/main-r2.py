import sys

def calc(expr: str) -> int | str:
    try:
        sys.set_int_max_str_digits(0)
    except Exception:
        pass
    sys.setrecursionlimit(10000)

    toks = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            toks.append(int(expr[i:j]))
            i = j
        else:
            toks.append(c)
            i += 1
    toks.append(None)
    pos = 0

    class Err(Exception):
        pass

    def parse_atom():
        nonlocal pos
        t = toks[pos]
        pos += 1
        if t == '(':
            v = parse_add()
            pos += 1  # ')'
            return v
        return t

    def parse_unary():
        nonlocal pos
        items = []
        while True:
            sign = 1
            while toks[pos] == '-':
                sign = -sign
                pos += 1
            atom = parse_atom()
            items.append((sign, atom))
            if toks[pos] == '^':
                pos += 1
            else:
                break
        s, a = items[-1]
        tail = s * a
        for k in range(len(items) - 2, -1, -1):
            s, a = items[k]
            if tail < 0:
                raise Err()
            tail = s * (a ** tail)
        return tail

    def parse_mul():
        nonlocal pos
        v = parse_unary()
        while toks[pos] in ('*', '/', '%'):
            op = toks[pos]
            pos += 1
            r = parse_unary()
            if op == '*':
                v = v * r
            else:
                if r == 0:
                    raise Err()
                q = abs(v) // abs(r)
                if (v < 0) != (r < 0):
                    q = -q
                if op == '/':
                    v = q
                else:
                    v = v - r * q
        return v

    def parse_add():
        nonlocal pos
        v = parse_mul()
        while toks[pos] in ('+', '-'):
            op = toks[pos]
            pos += 1
            r = parse_mul()
            v = v + r if op == '+' else v - r
        return v

    try:
        return parse_add()
    except Err:
        return "error"
