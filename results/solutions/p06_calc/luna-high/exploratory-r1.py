import sys


class _CalcError(Exception):
    pass


def calc(expr: str) -> int | str:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(expr) * 4 + 1000))

    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i].isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1

            digits = expr[i:j]
            value = 0
            first = len(digits) % 9
            if first:
                value = int(digits[:first])
            for k in range(first, len(digits), 9):
                value = value * 1_000_000_000 + int(digits[k:k + 9])

            tokens.append(value)
            i = j
        else:
            tokens.append(expr[i])
            i += 1

    pos = 0

    def primary():
        nonlocal pos
        token = tokens[pos]
        if token == '(':
            pos += 1
            value = additive()
            pos += 1  # ')'
            return value
        pos += 1
        return token

    def power():
        nonlocal pos
        base = primary()
        if pos < len(tokens) and tokens[pos] == '^':
            pos += 1
            exponent = unary()
            if exponent < 0:
                raise _CalcError
            base = pow(base, exponent)
        return base

    def unary():
        nonlocal pos
        if pos < len(tokens) and tokens[pos] == '-':
            pos += 1
            return -unary()
        return power()

    def multiplicative():
        nonlocal pos
        value = unary()
        while pos < len(tokens) and tokens[pos] in ('*', '/', '%'):
            op = tokens[pos]
            pos += 1
            rhs = unary()
            if op == '*':
                value *= rhs
            elif op == '/':
                if rhs == 0:
                    raise _CalcError
                quotient = abs(value) // abs(rhs)
                value = -quotient if (value < 0) != (rhs < 0) else quotient
            else:
                if rhs == 0:
                    raise _CalcError
                quotient = abs(value) // abs(rhs)
                if (value < 0) != (rhs < 0):
                    quotient = -quotient
                value -= rhs * quotient
        return value

    def additive():
        nonlocal pos
        value = multiplicative()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            rhs = multiplicative()
            value = value + rhs if op == '+' else value - rhs
        return value

    try:
        return additive()
    except _CalcError:
        return "error"
