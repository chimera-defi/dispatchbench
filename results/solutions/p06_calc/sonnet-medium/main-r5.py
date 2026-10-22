def calc(expr: str) -> int | str:
    s = expr.replace(" ", "")
    n = len(s)
    pos = 0

    class Err(Exception):
        pass

    def atom():
        nonlocal pos
        if s[pos] == '(':
            pos += 1
            v = parse_expr()
            pos += 1  # ')'
            return v
        st = pos
        while pos < n and s[pos].isdigit():
            pos += 1
        return int(s[st:pos])

    def minuses():
        nonlocal pos
        c = 0
        while pos < n and s[pos] == '-':
            c += 1
            pos += 1
        return -1 if c % 2 else 1

    def power():
        nonlocal pos
        a0 = atom()
        items = []
        while pos < n and s[pos] == '^':
            pos += 1
            sg = minuses()
            items.append((sg, atom()))
        if not items:
            return a0
        v = items[-1][0] * items[-1][1]
        for i in range(len(items) - 2, -1, -1):
            sg, a = items[i]
            if v < 0:
                raise Err
            v = sg * (a ** v)
        if v < 0:
            raise Err
        return a0 ** v

    def unary():
        sg = minuses()
        return sg * power()

    def parse_term():
        nonlocal pos
        v = unary()
        while pos < n and s[pos] in '*/%':
            op = s[pos]
            pos += 1
            b = unary()
            if op == '*':
                v = v * b
            else:
                if b == 0:
                    raise Err
                q = abs(v) // abs(b)
                if (v < 0) != (b < 0):
                    q = -q
                v = q if op == '/' else v - b * q
        return v

    def parse_expr():
        nonlocal pos
        v = parse_term()
        while pos < n and s[pos] in '+-':
            op = s[pos]
            pos += 1
            b = parse_term()
            v = v + b if op == '+' else v - b
        return v

    try:
        return parse_expr()
    except Err:
        return "error"
