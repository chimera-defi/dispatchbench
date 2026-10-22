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

    def minuses():
        nonlocal pos
        c = 0
        skip()
        while pos < n and s[pos] == '-':
            c += 1
            pos += 1
            skip()
        return c

    def atom():
        nonlocal pos
        skip()
        if s[pos] == '(':
            pos += 1
            v = parse_expr()
            skip()
            pos += 1  # ')'
            return v
        st = pos
        while pos < n and s[pos].isdigit():
            pos += 1
        return int(s[st:pos])

    def power():
        nonlocal pos
        bases = [atom()]
        signs = []
        while True:
            skip()
            if pos < n and s[pos] == '^':
                pos += 1
                signs.append(minuses() & 1)
                bases.append(atom())
            else:
                break
        val = bases[-1]
        for i in range(len(bases) - 2, -1, -1):
            e = -val if signs[i] else val
            if e < 0:
                raise Err
            val = bases[i] ** e
        return val

    def unary():
        c = minuses()
        v = power()
        return -v if c & 1 else v

    def parse_term():
        nonlocal pos
        v = unary()
        while True:
            skip()
            if pos < n and s[pos] in '*/%':
                op = s[pos]
                pos += 1
                r = unary()
                if op == '*':
                    v = v * r
                else:
                    if r == 0:
                        raise Err
                    q = abs(v) // abs(r)
                    if (v < 0) != (r < 0):
                        q = -q
                    v = q if op == '/' else v - r * q
            else:
                return v

    def parse_expr():
        nonlocal pos
        v = parse_term()
        while True:
            skip()
            if pos < n and s[pos] in '+-':
                op = s[pos]
                pos += 1
                r = parse_term()
                v = v + r if op == '+' else v - r
            else:
                return v

    try:
        return parse_expr()
    except Err:
        return "error"
