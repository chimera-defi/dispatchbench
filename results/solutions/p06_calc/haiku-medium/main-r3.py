def calc(expr: str) -> int | str:
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
            digits = expr[i:j]
            # Convert in chunks to stay under Python's int-from-str digit limit.
            v = 0
            for k in range(0, len(digits), 1000):
                chunk = digits[k:k + 1000]
                v = v * 10 ** len(chunk) + int(chunk)
            tokens.append(v)
            i = j
        else:
            tokens.append(c)
            i += 1
    tokens.append(None)  # end-of-input sentinel
    pos = 0

    def peek():
        return tokens[pos]

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def primary():
        tok = advance()
        if tok == '(':
            val = expr_()
            advance()  # consume ')'
            return val
        return tok

    def power():
        # Right-associative chain, folded iteratively to avoid deep recursion.
        # signs[k] is True if the operand at index k is preceded by an odd
        # number of unary minuses (only possible after '^').
        vals = [primary()]
        signs = [False]
        while peek() == '^':
            advance()
            neg = False
            while peek() == '-':
                advance()
                neg = not neg
            signs.append(neg)
            vals.append(primary())
        t = vals[-1]
        for j in range(len(vals) - 2, -1, -1):
            if signs[j + 1]:
                t = -t
            if t < 0:
                raise ValueError("negative exponent")
            t = vals[j] ** t
        return t

    def unary():
        neg = False
        while peek() == '-':
            advance()
            neg = not neg
        val = power()
        return -val if neg else val

    def term():
        val = unary()
        while peek() in ('*', '/', '%'):
            op = advance()
            rhs = unary()
            if op == '*':
                val = val * rhs
            else:
                if rhs == 0:
                    raise ValueError("division by zero")
                # Truncating division toward zero.
                q = abs(val) // abs(rhs)
                if (val < 0) != (rhs < 0):
                    q = -q
                val = q if op == '/' else val - rhs * q
        return val

    def expr_():
        val = term()
        while peek() in ('+', '-'):
            op = advance()
            rhs = term()
            val = val + rhs if op == '+' else val - rhs
        return val

    try:
        return expr_()
    except ValueError:
        return "error"
