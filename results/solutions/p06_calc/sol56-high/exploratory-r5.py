def calc(expr: str) -> int | str:
    precedence = {
        "+": 1, "-": 1,
        "*": 2, "/": 2, "%": 2,
        "u-": 3,
        "^": 4,
    }
    right_associative = {"^", "u-"}
    output = []
    operators = []
    expect_operand = True
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch == " ":
            i += 1
            continue

        if "0" <= ch <= "9":
            j = i + 1
            while j < n and "0" <= expr[j] <= "9":
                j += 1

            value = 0
            k = i
            while k < j:
                end = min(k + 9, j)
                block = expr[k:end]
                value = value * (10 ** len(block)) + int(block)
                k = end

            output.append(value)
            expect_operand = False
            i = j
            continue

        if ch == "(":
            operators.append(ch)
            expect_operand = True
        elif ch == ")":
            while operators[-1] != "(":
                output.append(operators.pop())
            operators.pop()
            expect_operand = False
        else:
            op = "u-" if ch == "-" and expect_operand else ch

            if op == "u-":
                operators.append(op)
                expect_operand = True
            else:
                p = precedence[op]
                while operators and operators[-1] != "(":
                    top = operators[-1]
                    if (precedence[top] > p or
                            (precedence[top] == p and
                             op not in right_associative)):
                        output.append(operators.pop())
                    else:
                        break
                operators.append(op)
                expect_operand = True

        i += 1

    while operators:
        output.append(operators.pop())

    stack = []
    error = None

    for token in output:
        if isinstance(token, int):
            stack.append(token)
            continue

        if token == "u-":
            value = stack.pop()
            stack.append(error if value is error else -value)
            continue

        b = stack.pop()
        a = stack.pop()

        if a is error or b is error:
            stack.append(error)
        elif token == "+":
            stack.append(a + b)
        elif token == "-":
            stack.append(a - b)
        elif token == "*":
            stack.append(a * b)
        elif token == "/":
            if b == 0:
                stack.append(error)
            else:
                quotient = abs(a) // abs(b)
                stack.append(-quotient if (a < 0) != (b < 0) else quotient)
        elif token == "%":
            if b == 0:
                stack.append(error)
            else:
                quotient = abs(a) // abs(b)
                if (a < 0) != (b < 0):
                    quotient = -quotient
                stack.append(a - b * quotient)
        else:
            if b < 0:
                stack.append(error)
            elif b == 0:
                stack.append(1)
            elif a == 0:
                stack.append(0)
            elif a == 1:
                stack.append(1)
            elif a == -1:
                stack.append(-1 if b & 1 else 1)
            else:
                stack.append(pow(a, b))

    return "error" if stack[0] is error else stack[0]
