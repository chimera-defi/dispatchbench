def calc(expr: str) -> int | str:
    values = []
    operators = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "~": 3, "^": 4}

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

    def parse_integer(start: int, end: int) -> int:
        value = 0
        first = (end - start) % 9
        pos = start

        if first:
            value = int(expr[pos:pos + first])
            pos += first

        while pos < end:
            value = value * 1_000_000_000 + int(expr[pos:pos + 9])
            pos += 9

        return value

    n = len(expr)
    i = 0
    expecting_operand = True

    while i < n:
        c = expr[i]

        if c == " ":
            i += 1
            continue

        if "0" <= c <= "9":
            j = i + 1
            while j < n and "0" <= expr[j] <= "9":
                j += 1
            values.append(parse_integer(i, j))
            i = j
            expecting_operand = False
            continue

        if c == "(":
            operators.append(c)
            expecting_operand = True
            i += 1
            continue

        if c == ")":
            while operators[-1] != "(":
                if not apply_operator():
                    return "error"
            operators.pop()
            expecting_operand = False
            i += 1
            continue

        if c == "-" and expecting_operand:
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
        expecting_operand = True
        i += 1

    while operators:
        if not apply_operator():
            return "error"

    return values[0]
