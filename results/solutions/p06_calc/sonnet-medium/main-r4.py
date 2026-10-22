def calc(expr: str) -> int | str:
    s = expr
    n = len(s)
    pos = 0

    class Err(Exception):
        pass

    def skip():
        nonlocal pos
        while pos < n and s[pos] == ' ':
            pos += 1

    def peek():
        skip()
        return s[pos] if pos < n else ''

    def minus_count():
        nonlocal pos
        c = 0
        while peek() == '-':
            c += 1
            pos += 1
        return c

    def atom():
        nonlocal pos
        ch = peek()
        if ch == '(':
            pos += 1
            v = expr_()
            skip()
            pos += 1  # ')'
            return v
        st = pos
        while pos < n and s[pos].isdigit():
            pos += 1
        return int(s[st:pos])

    def power():
        nonlocal pos
        items = [(0, atom())]
        while peek() == '^':
            pos += 1
            c = minus_count()
            items.append((c & 1, atom()))
        r = items[-1][1]
        for i in range(len(items) - 1, 0, -1):
            if items[i][0]:
                r = -r
            base = items[i - 1][1]
            if r < 0:
                raise Err()
            r = base ** r
        return r

    def unary():
        c = minus_count()
        v = power()
        return -v if c & 1 else v

    def term():
        nonlocal pos
        v = unary()
        while True:
            op = peek()
            if op not in ('*', '/', '%'):
                return v
            pos += 1
            w = unary()
            if op == '*':
                v = v * w
            else:
                if w == 0:
                    raise Err()
                q = abs(v) // abs(w)
                if (v < 0) != (w < 0):
                    q = -q
                v = q if op == '/' else v - w * q

    def expr_():
        nonlocal pos
        v = term()
        while True:
            op = peek()
            if op not in ('+', '-'):
                return v
            pos += 1
            w = term()
            v = v + w if op == '+' else v - w

    try:
        return expr_()
    except Err:
        return "error"
