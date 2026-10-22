import sys


class _CalcError(Exception):
    pass


def calc(expr: str) -> int | str:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)

    s = "".join(expr.split())
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if "0" <= c <= "9":
            j = i
            while j < n and "0" <= s[j] <= "9":
                j += 1
            tokens.append(int(s[i:j]))
            i = j
        else:
            tokens.append(c)
            i += 1

    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    def power(base, exp):
        if exp < 0:
            raise _CalcError
        return base ** exp

    def parse_expr():
        nonlocal pos
        value = parse_term()
        while peek() in ("+", "-"):
            op = tokens[pos]
            pos += 1
            rhs = parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term():
        nonlocal pos
        value = parse_unary()
        while peek() in ("*", "/", "%"):
            op = tokens[pos]
            pos += 1
            rhs = parse_unary()
            if op == "*":
                value = value * rhs
            else:
                if rhs == 0:
                    raise _CalcError
                q = trunc_div(value, rhs)
                value = q if op == "/" else value - rhs * q
        return value

    def parse_unary():
        nonlocal pos
        negs = 0
        while peek() == "-":
            pos += 1
            negs += 1
        value = parse_power()
        return -value if negs % 2 else value

    def parse_power():
        nonlocal pos
        vals = [parse_primary()]
        signs = [False]
        while peek() == "^":
            pos += 1
            negs = 0
            while peek() == "-":
                pos += 1
                negs += 1
            vals.append(parse_primary())
            signs.append(negs % 2 == 1)
        # Right-associative fold; a sign on an exponent applies to the whole tail.
        acc = vals[-1]
        for j in range(len(vals) - 2, -1, -1):
            exp = -acc if signs[j + 1] else acc
            acc = power(vals[j], exp)
        return acc

    def parse_primary():
        nonlocal pos
        tok = peek()
        if isinstance(tok, int):
            pos += 1
            return tok
        if tok == "(":
            pos += 1
            value = parse_expr()
            if peek() != ")":
                raise _CalcError
            pos += 1
            return value
        raise _CalcError

    try:
        result = parse_expr()
        if pos != len(tokens):
            return "error"
        return result
    except _CalcError:
        return "error"
