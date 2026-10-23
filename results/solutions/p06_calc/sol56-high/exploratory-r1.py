def calc(expr: str) -> int | str:
    values = []
    operators = []

    precedence = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2,
        "%": 2,
        "u-": 3,
        "^": 4,
    }

    def apply_operator(op: str) -> bool:
        if op == "u-":
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
        elif op in ("/", "%"):
            if b == 0:
                return False
            quotient = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                quotient = -quotient
            values.append(quotient if op == "/" else a - b * quotient)
        else:
            if b < 0:
                return False
            if a == 0:
                values.append(1 if b == 0 else 0)
            elif a == 1:
                values.append(1)
            elif a == -1:
                values.append(-1 if b & 1 else 1)
            else:
                values.append(pow(a, b))

        return True

    n = len(expr)
    i = 0
    expecting_operand = True

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            value = 0
            while i < n and expr[i].isdigit():
                value = value * 10 + (ord(expr[i]) - ord("0"))
                i += 1
            values.append(value)
            expecting_operand = False
            continue

        if ch == "(":
            operators.append(ch)
            expecting_operand = True
            i += 1
            continue

        if ch == ")":
            while operators[-1] != "(":
                if not apply_operator(operators.pop()):
                    return "error"
            operators.pop()
            expecting_operand = False
            i += 1
            continue

        if ch == "-" and expecting_operand:
            operators.append("u-")
            i += 1
            continue

        while operators and operators[-1] != "(":
            top = operators[-1]
            if precedence[top] > precedence[ch] or (
                precedence[top] == precedence[ch] and ch != "^"
            ):
                if not apply_operator(operators.pop()):
                    return "error"
            else:
                break

        operators.append(ch)
        expecting_operand = True
        i += 1

    while operators:
        if not apply_operator(operators.pop()):
            return "error"

    return values[0]
