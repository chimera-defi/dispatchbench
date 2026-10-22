def calc(expr: str) -> int | str:
    s = expr.replace(" ", "")
    n = len(s)
    pos = 0

    class Err(Exception):
        pass

    def tdiv(a, b):
        if b == 0:
            raise Err
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    def power(base, e):
        if e < 0:
            raise Err
        return base ** e

    def minuses():
        nonlocal pos
        c = 0
        while pos < n and s[pos] == '-':
            c += 1
            pos += 1
        return c

    def atom():
        nonlocal pos
        if s[pos] == '(':
            pos += 1
            v = add()
            pos += 1  # ')'
            return v
        st = pos
        while pos < n and s[pos].isdigit():
            pos += 1
        return int(s[st:pos])

    def pw():
        nonlocal pos
        a0 = atom()
        items = []
        while pos < n and s[pos] == '^':
            pos += 1
            sg = minuses()
            items.append((sg, atom()))
        if not items:
            return a0
        val = None
        for sg, a in reversed(items):
            cur = a if val is None else power(a, val)
            if sg % 2:
                cur = -cur
            val = cur
        return power(a0, val)

    def unary():
        c = minuses()
        v = pw()
        return -v if c % 2 else v

    def term():
        nonlocal pos
        v = unary()
        while pos < n and s[pos] in '*/%':
            op = s[pos]
            pos += 1
            r = unary()
            if op == '*':
                v = v * r
            elif op == '/':
                v = tdiv(v, r)
            else:
                v = v - r * tdiv(v, r)
        return v

    def add():
        nonlocal pos
        v = term()
        while pos < n and s[pos] in '+-':
            op = s[pos]
            pos += 1
            r = term()
            v = v + r if op == '+' else v - r
        return v

    try:
        return add()
    except Err:
        return "error"
