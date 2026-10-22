def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    token_pattern = re.compile(
        r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[()+*/,:=<>-]"
    )
    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "~": 3,
        ":": 4,
    }

    def parse(text):
        values = []
        operators = []
        expect_operand = True

        def reduce_operator():
            op = operators.pop()
            if op == "~":
                values.append(("~", values.pop()))
            else:
                right = values.pop()
                left = values.pop()
                values.append((op, left, right))

        for token in token_pattern.findall(text):
            if token[0].isdigit():
                values.append(("number", int(token)))
                expect_operand = False
            elif token in functions:
                operators.append(token)
                expect_operand = True
            elif token[0].isalpha():
                values.append(("reference", token))
                expect_operand = False
            elif token == "(":
                # The second item counts commas in this pair of parentheses.
                operators.append(["(", 0])
                expect_operand = True
            elif token == ",":
                while not isinstance(operators[-1], list):
                    reduce_operator()
                operators[-1][1] += 1
                expect_operand = True
            elif token == ")":
                while not isinstance(operators[-1], list):
                    reduce_operator()
                marker = operators.pop()
                if operators and operators[-1] in functions:
                    function = operators.pop()
                    count = marker[1] + 1
                    arguments = tuple(values[-count:])
                    del values[-count:]
                    values.append((function, arguments))
                expect_operand = False
            elif token == "-" and expect_operand:
                operators.append("~")
            else:
                while (
                    operators
                    and isinstance(operators[-1], str)
                    and operators[-1] in precedence
                    and precedence[operators[-1]] >= precedence[token]
                ):
                    reduce_operator()
                operators.append(token)
                expect_operand = True

        while operators:
            reduce_operator()
        return values[0]

    results = {}
    active = set()

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if name in results:
            return results[name]
        if name in active:
            return "#CYCLE!"

        active.add(name)
        content = cells[name].strip()
        if content.startswith("="):
            value = yield ("node", parse(content[1:]))
        else:
            value = int(content)

        active.remove(name)
        results[name] = value
        return value

    def evaluate_node(node):
        kind = node[0]

        if kind == "number":
            return node[1]

        if kind == "reference":
            return (yield ("cell", node[1]))

        if kind == "~":
            value = yield ("node", node[1])
            return value if isinstance(value, str) else -value

        if kind == "IF":
            condition, then_node, else_node = node[1]
            value = yield ("node", condition)
            if isinstance(value, str):
                return value
            return (yield ("node", then_node if value else else_node))

        if kind in {"SUM", "MIN", "MAX"}:
            aggregate = None

            for argument in node[1]:
                if argument[0] == ":":
                    first = argument[1][1]
                    last = argument[2][1]
                    left, right = sorted((ord(first[0]), ord(last[0])))
                    top, bottom = sorted((int(first[1:]), int(last[1:])))
                    requests = (
                        ("cell", chr(column) + str(row))
                        for row in range(top, bottom + 1)
                        for column in range(left, right + 1)
                        if chr(column) + str(row) in cells
                    )
                else:
                    requests = (("node", argument),)

                for request in requests:
                    value = yield request
                    if isinstance(value, str):
                        return value
                    if aggregate is None:
                        aggregate = value
                    elif kind == "SUM":
                        aggregate += value
                    elif kind == "MIN":
                        aggregate = min(aggregate, value)
                    else:
                        aggregate = max(aggregate, value)

            return 0 if aggregate is None else aggregate

        left = yield ("node", node[1])
        if isinstance(left, str):
            return left

        right = yield ("node", node[2])
        if isinstance(right, str):
            return right

        if kind == "+":
            return left + right
        if kind == "-":
            return left - right
        if kind == "*":
            return left * right
        if kind == "/":
            if right == 0:
                return "#DIV/0!"
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "=":
            return int(left == right)
        if kind == "<>":
            return int(left != right)
        if kind == "<":
            return int(left < right)
        if kind == "<=":
            return int(left <= right)
        if kind == ">":
            return int(left > right)
        if kind == ">=":
            return int(left >= right)

    # Drive generators explicitly so long reference chains and deeply nested
    # formulas do not consume Python's recursion stack.
    for name in cells:
        if name in results:
            continue

        stack = [evaluate_cell(name)]
        value = None

        while stack:
            try:
                request = stack[-1].send(value)
            except StopIteration as finished:
                stack.pop()
                value = finished.value
            else:
                request_kind, payload = request
                if request_kind == "cell":
                    stack.append(evaluate_cell(payload))
                else:
                    stack.append(evaluate_node(payload))
                value = None

    return {name: results[name] for name in cells}
