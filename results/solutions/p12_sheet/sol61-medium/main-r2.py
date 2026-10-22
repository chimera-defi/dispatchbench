def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    token_pattern = re.compile(r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[+\-*/():,=<>]")
    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "~": 3,
        ":": 4,
    }

    def parse(formula):
        nodes = []
        operators = []
        expect_operand = True

        def apply_operator():
            op = operators.pop()
            if op == "~":
                nodes.append(("neg", nodes.pop()))
            else:
                right = nodes.pop()
                left = nodes.pop()
                if op == ":":
                    nodes.append(("range", left[1], right[1]))
                else:
                    nodes.append(("binary", op, left, right))

        for token in token_pattern.findall(formula):
            if token[0].isdigit():
                nodes.append(("number", int(token)))
                expect_operand = False
            elif token in functions:
                operators.append(token)
                expect_operand = True
            elif token[0].isalpha():
                nodes.append(("ref", token))
                expect_operand = False
            elif token == "(":
                operators.append(["(", 0])
                expect_operand = True
            elif token == ",":
                while isinstance(operators[-1], str):
                    apply_operator()
                operators[-1][1] += 1
                expect_operand = True
            elif token == ")":
                while isinstance(operators[-1], str):
                    apply_operator()
                opening = operators.pop()
                if operators and operators[-1] in functions:
                    function = operators.pop()
                    count = opening[1] + 1
                    arguments = nodes[-count:]
                    del nodes[-count:]
                    nodes.append(("function", function, arguments))
                expect_operand = False
            else:
                op = "~" if token == "-" and expect_operand else token
                while (
                    operators
                    and isinstance(operators[-1], str)
                    and operators[-1] in precedence
                    and (
                        precedence[operators[-1]] > precedence[op]
                        or (
                            precedence[operators[-1]] == precedence[op]
                            and op != "~"
                        )
                    )
                ):
                    apply_operator()
                operators.append(op)
                expect_operand = True

        while operators:
            apply_operator()
        return nodes[0]

    def expand_arguments(arguments):
        for node in arguments:
            if node[0] != "range":
                yield node
                continue

            first, last = node[1], node[2]
            col1, col2 = sorted((ord(first[0]), ord(last[0])))
            row1, row2 = sorted((int(first[1:]), int(last[1:])))
            for row in range(row1, row2 + 1):
                for col in range(col1, col2 + 1):
                    name = chr(col) + str(row)
                    if name in cells:
                        yield ("ref", name)

    states = {}
    results = {}
    values = []
    tasks = []

    for root in cells:
        if states.get(root) == 2:
            continue

        tasks.append(("cell", root))

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "cell":
                name = task[1]
                if name not in cells:
                    values.append(0)
                elif states.get(name) == 2:
                    values.append(results[name])
                elif states.get(name) == 1:
                    values.append("#CYCLE!")
                else:
                    states[name] = 1
                    tasks.append(("finish_cell", name))
                    content = cells[name].strip()
                    if content.startswith("="):
                        tasks.append(("eval", parse(content[1:])))
                    else:
                        values.append(int(content))

            elif kind == "finish_cell":
                name = task[1]
                results[name] = values[-1]
                states[name] = 2

            elif kind == "eval":
                node = task[1]
                node_kind = node[0]

                if node_kind == "number":
                    values.append(node[1])
                elif node_kind == "ref":
                    tasks.append(("cell", node[1]))
                elif node_kind == "neg":
                    tasks.append(("negate",))
                    tasks.append(("eval", node[1]))
                elif node_kind == "binary":
                    tasks.append(("binary_left", node[1], node[3]))
                    tasks.append(("eval", node[2]))
                else:
                    function, arguments = node[1], node[2]
                    if function == "IF":
                        tasks.append(("choose", arguments[1], arguments[2]))
                        tasks.append(("eval", arguments[0]))
                    else:
                        tasks.append((
                            "aggregate",
                            function,
                            expand_arguments(arguments),
                            0 if function == "SUM" else None,
                        ))

            elif kind == "negate":
                value = values.pop()
                values.append(value if isinstance(value, str) else -value)

            elif kind == "binary_left":
                left = values.pop()
                if isinstance(left, str):
                    values.append(left)
                else:
                    tasks.append(("binary_right", task[1], left))
                    tasks.append(("eval", task[2]))

            elif kind == "binary_right":
                right = values.pop()
                op, left = task[1], task[2]

                if isinstance(right, str):
                    values.append(right)
                elif op == "+":
                    values.append(left + right)
                elif op == "-":
                    values.append(left - right)
                elif op == "*":
                    values.append(left * right)
                elif op == "/":
                    if right == 0:
                        values.append("#DIV/0!")
                    else:
                        quotient = abs(left) // abs(right)
                        values.append(
                            -quotient if (left < 0) != (right < 0) else quotient
                        )
                elif op == "=":
                    values.append(int(left == right))
                elif op == "<>":
                    values.append(int(left != right))
                elif op == "<":
                    values.append(int(left < right))
                elif op == "<=":
                    values.append(int(left <= right))
                elif op == ">":
                    values.append(int(left > right))
                else:
                    values.append(int(left >= right))

            elif kind == "choose":
                condition = values.pop()
                if isinstance(condition, str):
                    values.append(condition)
                else:
                    tasks.append(("eval", task[1] if condition else task[2]))

            elif kind == "aggregate":
                function, iterator, accumulated = task[1:]
                node = next(iterator, None)
                if node is None:
                    values.append(0 if accumulated is None else accumulated)
                else:
                    tasks.append((
                        "aggregate_value", function, iterator, accumulated
                    ))
                    tasks.append(("eval", node))

            elif kind == "aggregate_value":
                value = values.pop()
                function, iterator, accumulated = task[1:]

                if isinstance(value, str):
                    values.append(value)
                else:
                    if function == "SUM":
                        accumulated += value
                    elif accumulated is None:
                        accumulated = value
                    elif function == "MIN":
                        accumulated = min(accumulated, value)
                    else:
                        accumulated = max(accumulated, value)

                    tasks.append((
                        "aggregate", function, iterator, accumulated
                    ))

        values.pop()

    return {name: results[name] for name in cells}
