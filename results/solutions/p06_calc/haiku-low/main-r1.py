import sys


def calc(expr: str) -> int | str:
    # Deep chains of ^ or unary minus recurse once per operator.
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 30000))

    tokens = []
    i, n = 0, len(expr)
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

    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def take():
        nonlocal pos
        t = tokens[pos]
        pos += 1
        return t

    def primary():
        t = peek()
        if isinstance(t, int):
            take()
            return t
        take()  # '('
        v = additive()
        take()  # ')'
        return v

    def power():
        base = primary()
        if peek() == '^':
            take()
            exp = unary()  # right operand may start with unary minus
            if exp < 0:
                raise ArithmeticError("negative power")
            return base ** exp  # right-assoc via recursion through unary()
        return base

    def unary():
        neg = False
        while peek() == '-':
            take()
            neg = not neg
        v = power()
        return -v if neg else v

    def term():
        v = unary()
        while peek() in ('*', '/', '%'):
            op = take()
            r = unary()
            if op == '*':
                v = v * r
            else:
                if r == 0:
                    raise ZeroDivisionError("division by zero")
                q = abs(v) // abs(r)  # truncate toward zero
                if (v < 0) != (r < 0):
                    q = -q
                if op == '/':
                    v = q
                else:
                    v = v - r * q
        return v

    def additive():
        v = term()
        while peek() in ('+', '-'):
            op = take()
            r = term()
            v = v + r if op == '+' else v - r
        return v

    try:
        return additive()
    except ArithmeticError:
        return "error"
