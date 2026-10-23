def calc(expr: str) -> int | str:
    values = []
    operators = []

    precedence = {
        "+": 1, "-": 1,
        "*": 2, "/": 2, "%": 2,
        "~": 3,
        "^": 4,
    }

    def apply_operator() -> bool:
        op = operators.pop()

        if op == "~":
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
            values.append(-q if (a < 0) != (b < 0) else q)
        elif op == "%":
            if b == 0:
                return False
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                q = -q
            values.append(a - b * q)
        else:
            if b < 0:
                return False
            values.append(pow(a, b))

        return True

    i = 0
    n = len(expr)
    expect_operand = True

    while i < n:
        c = expr[i]

        if c.isspace():
            i += 1
            continue

        if c.isdigit():
            value = 0
            while i < n and expr[i].isdigit():
                value = value * 10 + (ord(expr[i]) - 48)
                i += 1
            values.append(value)
            expect_operand = False
            continue

        if c == "(":
            operators.append(c)
            expect_operand = True
            i += 1
            continue

        if c == ")":
            while operators[-1] != "(":
                if not apply_operator():
                    return "error"
            operators.pop()
            expect_operand = False
            i += 1
            continue

        if c == "-" and expect_operand:
            operators.append("~")
            i += 1
            continue

        while operators and operators[-1] != "(":
            top = operators[-1]
            if precedence[top] > precedence[c] or (
                precedence[top] == precedence[c] and c != "^"
            ):
                if not apply_operator():
                    return "error"
            else:
                break

        operators.append(c)
        expect_operand = True
        i += 1

    while operators:
        if not apply_operator():
            return "error"

    return values[0]
