def calc(expr: str) -> int | str:
    class _Error(Exception):
        pass

    # Tokenize: integers (as int) and single-character operators/parentheses.
    # Digit strings are converted in chunks so very long literals avoid
    # Python's int-from-str digit limit.
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c == " ":
            i += 1
        elif "0" <= c <= "9":
            j = i
            while j < n and "0" <= expr[j] <= "9":
                j += 1
            digits = expr[i:j]
            value = 0
            for k in range(0, len(digits), 1000):
                chunk = digits[k:k + 1000]
                value = value * 10 ** len(chunk) + int(chunk)
            tokens.append(value)
            i = j
        else:
            tokens.append(c)
            i += 1

    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def expr_rule():
        nonlocal pos
        v = term()
        while peek() in ("+", "-"):
            op = peek()
            pos += 1
            r = term()
            v = v + r if op == "+" else v - r
        return v

    def term():
        nonlocal pos
        v = unary()
        while peek() in ("*", "/", "%"):
            op = peek()
            pos += 1
            r = unary()
            if op == "*":
                v = v * r
            else:
                if r == 0:
                    raise _Error()
                # Truncating division toward zero.
                q = abs(v) // abs(r)
                if (v < 0) != (r < 0):
                    q = -q
                v = q if op == "/" else v - r * q
        return v

    def unary():
        nonlocal pos
        negate = False
        while peek() == "-":
            negate = not negate
            pos += 1
        v = power()
        return -v if negate else v

    def power():
        nonlocal pos
        # Collect the chain base0 ^ [-]* base1 ^ [-]* base2 ... iteratively
        # so long chains do not consume Python recursion depth.
        bases = [primary()]
        signs = []  # signs[i] is the parity of minus signs before bases[i+1]
        while peek() == "^":
            pos += 1
            count = 0
            while peek() == "-":
                count += 1
                pos += 1
            signs.append(count % 2)
            bases.append(primary())
        # Right-associative fold.
        val = bases[-1]
        for i in range(len(bases) - 2, -1, -1):
            e = -val if signs[i] else val
            if e < 0:
                raise _Error()
            val = bases[i] ** e
        return val

    def primary():
        nonlocal pos
        tok = peek()
        if isinstance(tok, int):
            pos += 1
            return tok
        if tok == "(":
            pos += 1
            v = expr_rule()
            if peek() != ")":
                raise _Error()
            pos += 1
            return v
        raise _Error()

    try:
        result = expr_rule()
        if pos != len(tokens):
            raise _Error()
        return result
    except (_Error, ZeroDivisionError):
        return "error"
