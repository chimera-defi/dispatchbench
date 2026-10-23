def calc(expr: str) -> int | str:
    values = []
    ops = []

    precedence = {
        "^": 4,
        "u": 3,
        "*": 2,
        "/": 2,
        "%": 2,
        "+": 1,
        "-": 1,
    }

    def apply_top():
        op = ops.pop()

        if op == "u":
            values.append(-values.pop())
            return True

        b = values.pop()
        a = values.pop()

        if op == "+":
            values.append(a + b)
        elif op == "-":
            values.append(a - b)
        elif op == "*":
            values.append(a * b)
        elif op == "/":
            if b == 0:
                return False
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                q = -q
            values.append(q)
        elif op == "%":
            if b == 0:
                return False
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                q = -q
            values.append(a - b * q)
        else:  # "^"
            if b < 0:
                return False
            values.append(pow(a, b))

        return True

    i = 0
    expect_operand = True
    n = len(expr)

    while i < n:
        c = expr[i]

        if c.isspace():
            i += 1
            continue

        if "0" <= c <= "9":
            value = 0
            while i < n and "0" <= expr[i] <= "9":
                value = value * 10 + ord(expr[i]) - ord("0")
                i += 1
            values.append(value)
            expect_operand = False
            continue

        if c == "(":
            ops.append(c)
            expect_operand = True
            i += 1
            continue

        if c == ")":
            while ops[-1] != "(":
                if not apply_top():
                    return "error"
            ops.pop()
            expect_operand = False
            i += 1
            continue

        if c == "-" and expect_operand:
            ops.append("u")
            i += 1
            continue

        if c in "+-*/%^":
            while (
                ops
                and ops[-1] != "("
                and precedence[ops[-1]] >= precedence[c]
            ):
                if not apply_top():
                    return "error"
            ops.append(c)
            expect_operand = True
            i += 1
            continue

        i += 1

    while ops:
        if not apply_top():
            return "error"

    return values[0]
