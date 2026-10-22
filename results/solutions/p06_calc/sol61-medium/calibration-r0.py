def calc(expr: str) -> int | str:
    values = []
    operators = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "neg": 3, "^": 4}

    def apply() -> bool:
        op = operators.pop()
        if op == "neg":
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
    expecting_operand = True

    while i < len(expr):
        c = expr[i]

        if c == " ":
            i += 1
            continue

        if "0" <= c <= "9":
            # Avoid Python's limit on decimal string-to-int conversion.
            number = 0
            while i < len(expr) and "0" <= expr[i] <= "9":
                number = number * 10 + ord(expr[i]) - ord("0")
                i += 1
            values.append(number)
            expecting_operand = False
            continue

        if c == "(":
            operators.append(c)
            expecting_operand = True
        elif c == ")":
            while operators[-1] != "(":
                if not apply():
                    return "error"
            operators.pop()
            expecting_operand = False
        elif c == "-" and expecting_operand:
            # Prefix minus never reduces a pending power operator.
            operators.append("neg")
        else:
            while operators and operators[-1] != "(":
                top = precedence[operators[-1]]
                current = precedence[c]
                if top < current or (top == current and c == "^"):
                    break
                if not apply():
                    return "error"
            operators.append(c)
            expecting_operand = True

        i += 1

    while operators:
        if not apply():
            return "error"

    return values[0]
