def calc(expr: str) -> int | str:
    class EvalError(Exception):
        pass

    n = len(expr)
    pos = 0

    def skip_spaces():
        nonlocal pos
        while pos < n and expr[pos] == " ":
            pos += 1

    def parse_add():
        nonlocal pos
        value = parse_mul()
        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "+-":
                return value
            op = expr[pos]
            pos += 1
            rhs = parse_mul()
            value = value + rhs if op == "+" else value - rhs

    def parse_mul():
        nonlocal pos
        value = parse_unary()
        while True:
            skip_spaces()
            if pos >= n or expr[pos] not in "*/%":
                return value
            op = expr[pos]
            pos += 1
            rhs = parse_unary()
            if rhs == 0:
                raise EvalError
            if op == "*":
                value *= rhs
            else:
                quotient = abs(value) // abs(rhs)
                if (value < 0) != (rhs < 0):
                    quotient = -quotient
                if op == "/":
                    value = quotient
                else:
                    value = value - rhs * quotient

    def parse_unary():
        nonlocal pos
        skip_spaces()
        if pos < n and expr[pos] == "-":
            pos += 1
            return -parse_unary()
        return parse_power()

    def parse_power():
        nonlocal pos
        base = parse_atom()
        skip_spaces()
        if pos < n and expr[pos] == "^":
            pos += 1
            exponent = parse_unary()
            if exponent < 0:
                raise EvalError
            base = pow(base, exponent)
        return base

    def parse_atom():
        nonlocal pos
        skip_spaces()
        if expr[pos] == "(":
            pos += 1
            value = parse_add()
            skip_spaces()
            pos += 1
            return value

        value = 0
        while pos < n and "0" <= expr[pos] <= "9":
            value = value * 10 + ord(expr[pos]) - ord("0")
            pos += 1
        return value

    try:
        return parse_add()
    except EvalError:
        return "error"
