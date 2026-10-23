def calc(expr: str) -> int | str:
    values = []
    operators = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "~": 3, "^": 4}

    def apply():
        op = operators.pop()
        if op == "~":
            values[-1] = -values[-1]
            return

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
                raise ValueError
            result = pow(a, b)
        else:
            if b == 0:
                raise ValueError
            quotient = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                quotient = -quotient
            result = quotient if op == "/" else a - b * quotient

        values.append(result)

    i = 0
    expect_operand = True

    try:
        while i < len(expr):
            ch = expr[i]

            if ch == " ":
                i += 1
                continue

            if "0" <= ch <= "9":
                number = 0
                while i < len(expr) and "0" <= expr[i] <= "9":
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
                    apply()
                operators.pop()
                expect_operand = False
            elif ch == "-" and expect_operand:
                # Prefix minus never reduces a pending power operator.
                operators.append("~")
            else:
                while operators and operators[-1] != "(":
                    top = operators[-1]
                    if precedence[top] > precedence[ch] or (
                        precedence[top] == precedence[ch] and ch != "^"
                    ):
                        apply()
                    else:
                        break
                operators.append(ch)
                expect_operand = True

            i += 1

        while operators:
            apply()

        return values[0]
    except ValueError:
        return "error"
