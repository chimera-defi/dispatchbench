def calc(expr: str) -> int | str:
    precedence = {"^": 4, "u-": 3, "*": 2, "/": 2, "%": 2, "+": 1, "-": 1}
    right_associative = {"^"}

    values = []
    operators = []
    i = 0
    expect_operand = True

    def apply():
        op = operators.pop()
        if op == "u-":
            values.append(-values.pop())
            return

        b = values.pop()
        a = values.pop()

        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            if b == 0:
                raise ZeroDivisionError
            q = abs(a) // abs(b)
            result = -q if (a < 0) != (b < 0) else q
        elif op == "%":
            if b == 0:
                raise ZeroDivisionError
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                q = -q
            result = a - b * q
        else:  # ^
            if b < 0:
                raise ValueError
            result = a ** b

        values.append(result)

    try:
        while i < len(expr):
            ch = expr[i]

            if ch.isspace():
                i += 1
            elif ch.isdigit():
                start = i
                while i < len(expr) and expr[i].isdigit():
                    i += 1

                literal = 0
                digits = expr[start:i]
                first = len(digits) % 9 or 9
                literal = int(digits[:first])
                for j in range(first, len(digits), 9):
                    literal = literal * 1_000_000_000 + int(digits[j:j + 9])

                values.append(literal)
                expect_operand = False
            elif ch == "(":
                operators.append(ch)
                i += 1
                expect_operand = True
            elif ch == ")":
                while operators[-1] != "(":
                    apply()
                operators.pop()
                i += 1
                expect_operand = False
            else:
                if ch == "-" and expect_operand:
                    operators.append("u-")
                    i += 1
                    continue

                while (
                    operators
                    and operators[-1] != "("
                    and (
                        precedence[operators[-1]] > precedence[ch]
                        or (
                            precedence[operators[-1]] == precedence[ch]
                            and ch not in right_associative
                        )
                    )
                ):
                    apply()

                operators.append(ch)
                i += 1
                expect_operand = True

        while operators:
            apply()

        return values[0]
    except (ZeroDivisionError, ValueError):
        return "error"
