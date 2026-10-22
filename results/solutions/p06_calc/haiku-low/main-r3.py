import sys


class _CalcError(Exception):
    pass


def calc(expr: str) -> int | str:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c == ' ':
            i += 1
        elif '0' <= c <= '9':
            j = i
            while j < n and '0' <= expr[j] <= '9':
                j += 1
            tokens.append(int(expr[i:j]))
            i = j
        else:
            tokens.append(c)
            i += 1

    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def advance():
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def trunc_div(a, b):
        if b == 0:
            raise _CalcError()
        q = abs(a) // abs(b)
        return q if (a >= 0) == (b >= 0) else -q

    def parse_expr():
        v = parse_term()
        while peek() in ('+', '-'):
            op = advance()
            r = parse_term()
            v = v + r if op == '+' else v - r
        return v

    def parse_term():
        v = parse_unary()
        while peek() in ('*', '/', '%'):
            op = advance()
            r = parse_unary()
            if op == '*':
                v = v * r
            elif op == '/':
                v = trunc_div(v, r)
            else:
                v = v - r * trunc_div(v, r)
        return v

    def parse_unary():
        neg = False
        while peek() == '-':
            advance()
            neg = not neg
        v = parse_power()
        return -v if neg else v

    def parse_power():
        base = parse_primary()
        if peek() == '^':
            advance()
            e = parse_unary()  # right-assoc; right operand may be negated
            if e < 0:
                raise _CalcError()
            return base ** e
        return base

    def parse_primary():
        t = advance()
        if t == '(':
            v = parse_expr()
            advance()  # ')'
            return v
        return t  # integer literal

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 20000))
    try:
        result = parse_expr()
    except _CalcError:
        return "error"
    finally:
        sys.setrecursionlimit(old_limit)
    return result
