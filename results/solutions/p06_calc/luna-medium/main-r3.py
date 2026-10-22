def calc(expr: str) -> int | str:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(expr) * 2 + 100))

    class EvaluationError(Exception):
        pass

    i = 0
    n = len(expr)

    def skip_spaces():
        nonlocal i
        while i < n and expr[i] == " ":
            i += 1

    def parse_primary():
        nonlocal i
        skip_spaces()

        if expr[i] == "(":
            i += 1
            value = parse_sum()
            skip_spaces()
            i += 1  # closing parenthesis
            return value

        start = i
        while i < n and "0" <= expr[i] <= "9":
            i += 1
        return int(expr[start:i])

    def parse_power():
        nonlocal i
        value = parse_primary()
        skip_spaces()
        if i < n and expr[i] == "^":
            i += 1
            exponent = parse_unary()
            if exponent < 0:
                raise EvaluationError
            value = value ** exponent
        return value

    def parse_unary():
        nonlocal i
        skip_spaces()
        if i < n and expr[i] == "-":
            i += 1
            return -parse_unary()
        return parse_power()

    def parse_product():
        nonlocal i
        value = parse_unary()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "*/%":
                return value

            op = expr[i]
            i += 1
            rhs = parse_unary()

            if op == "*":
                value *= rhs
            else:
                if rhs == 0:
                    raise EvaluationError
                quotient = abs(value) // abs(rhs)
                if (value < 0) != (rhs < 0):
                    quotient = -quotient
                value = quotient if op == "/" else value - rhs * quotient

    def parse_sum():
        nonlocal i
        value = parse_product()

        while True:
            skip_spaces()
            if i >= n or expr[i] not in "+-":
                return value

            op = expr[i]
            i += 1
            rhs = parse_product()
            value = value + rhs if op == "+" else value - rhs

    try:
        result = parse_sum()
        return result
    except EvaluationError:
        return "error"
