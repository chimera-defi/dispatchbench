def calc(expr: str) -> int | str:
    ERROR = object()
    values = []
    operators = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "u": 3, "^": 4}

    def apply_operator(op: str) -> None:
        if op == "u":
            value = values.pop()
            values.append(ERROR if value is ERROR else -value)
            return

        right = values.pop()
        left = values.pop()

        if left is ERROR or right is ERROR:
            values.append(ERROR)
            return

        if op == "+":
            result = left + right
        elif op == "-":
            result = left - right
        elif op == "*":
            result = left * right
        elif op == "^":
            result = ERROR if right < 0 else pow(left, right)
        elif right == 0:
            result = ERROR
        else:
            quotient = abs(left) // abs(right)
            if (left < 0) != (right < 0):
                quotient = -quotient
            result = quotient if op == "/" else left - right * quotient

        values.append(result)

    def parse_integer(start: int, end: int) -> int:
        first_length = (end - start) % 9 or 9
        position = start + first_length
        value = int(expr[start:position])
        while position < end:
            value = value * 1_000_000_000 + int(expr[position:position + 9])
            position += 9
        return value

    i = 0
    expecting_operand = True

    while i < len(expr):
        char = expr[i]

        if char == " ":
            i += 1
            continue

        if char.isdigit():
            end = i + 1
            while end < len(expr) and expr[end].isdigit():
                end += 1
            values.append(parse_integer(i, end))
            i = end
            expecting_operand = False
            continue

        if char == "(":
            operators.append(char)
            expecting_operand = True
            i += 1
            continue

        if char == ")":
            while operators[-1] != "(":
                apply_operator(operators.pop())
            operators.pop()
            expecting_operand = False
            i += 1
            continue

        if char == "-" and expecting_operand:
            operators.append("u")
            i += 1
            continue

        while operators and operators[-1] != "(":
            top = operators[-1]
            if precedence[top] < precedence[char]:
                break
            if precedence[top] == precedence[char] and char == "^":
                break
            apply_operator(operators.pop())

        operators.append(char)
        expecting_operand = True
        i += 1

    while operators:
        apply_operator(operators.pop())

    return "error" if values[0] is ERROR else values[0]
