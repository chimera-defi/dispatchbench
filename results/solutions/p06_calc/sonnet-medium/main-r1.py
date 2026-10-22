def calc(expr: str) -> int | str:
    s = expr
    n = len(s)
    pos = [0]

    class Err(Exception):
        pass

    def skip():
        while pos[0] < n and s[pos[0]] == ' ':
            pos[0] += 1

    def peek():
        skip()
        return s[pos[0]] if pos[0] < n else ''

    def minuses():
        c = 0
        while peek() == '-':
            c += 1
            pos[0] += 1
        return -1 if c % 2 else 1

    def atom():
        ch = peek()
        if ch == '(':
            pos[0] += 1
            v = parse_expr()
            skip()
            pos[0] += 1  # ')'
            return v
        i = pos[0]
        while i < n and s[i].isdigit():
            i += 1
        v = int(s[pos[0]:i])
        pos[0] = i
        return v

    def power():
        base = atom()
        items = []
        while peek() == '^':
            pos[0] += 1
            sg = minuses()
            items.append((sg, atom()))
        if not items:
            return base
        r = items[-1][0] * items[-1][1]
        for k in range(len(items) - 2, -1, -1):
            if r < 0:
                raise Err
            r = items[k][0] * pow(items[k][1], r)
        if r < 0:
            raise Err
        return pow(base, r)

    def unary():
        sg = minuses()
        return sg * power()

    def parse_term():
        v = unary()
        while True:
            op = peek()
            if op in ('*', '/', '%'):
                pos[0] += 1
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
            else:
                return v

    def parse_expr():
        v = parse_term()
        while True:
            op = peek()
            if op == '+':
                pos[0] += 1
                v += parse_term()
            elif op == '-':
                pos[0] += 1
                v -= parse_term()
            else:
                return v

    try:
        return parse_expr()
    except Err:
        return "error"
