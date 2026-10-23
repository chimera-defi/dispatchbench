def calc(expr: str) -> int | str:
    values = []
    operators = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "~": 3, "^": 4}

    def apply() -> bool:
        op = operators.pop()
        if op == "~":
            values[-1] = -values[-1]
            return True

        b = values.pop()
        a = values.pop()

        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "^":
            if b < 0:
                return False
            result = pow(a, b)
        else:
            if b == 0:
                return False
            quotient = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                quotient = -quotient
            result = quotient if op == "/" else a - b * quotient

        values.append(result)
        return True

    i = 0
    n = len(expr)
    expect_operand = True

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if "0" <= ch <= "9":
            number = 0
            while i < n and "0" <= expr[i] <= "9":
                number = number * 10 + ord(expr[i]) - ord("0")
                i += 1
            values.append(number)
            expect_operand = False
            continue

        if ch == "(":
            operators.append(ch)
            expect_operand = True
        elif ch == ")":
            while operators[-1] != "(":
                if not apply():
                    return "error"
            operators.pop()
            expect_operand = False
        elif ch == "-" and expect_operand:
            # Prefix minus must not pop a pending power operator.
            operators.append("~")
        else:
            while operators and operators[-1] != "(":
                top = precedence[operators[-1]]
                current = precedence[ch]
                if top < current or (top == current and ch == "^"):
                    break
                if not apply():
                    return "error"
            operators.append(ch)
            expect_operand = True

        i += 1

    while operators:
        if not apply():
            return "error"

    return values[0]
