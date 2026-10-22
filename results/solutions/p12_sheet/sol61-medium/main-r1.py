import re


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    token_pattern = re.compile(r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[+\-*/():,=<>]")
    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "neg": 3,
        ":": 4,
    }

    def parse(formula):
        nodes = []
        operators = []
        argument_counts = []
        expect_operand = True

        def reduce_operator():
            op = operators.pop()
            if op == "neg":
                nodes.append(("neg", nodes.pop()))
                return
            right = nodes.pop()
            left = nodes.pop()
            if op == ":":
                nodes.append(("range", left[1], right[1]))
            else:
                nodes.append(("binary", op, left, right))

        for token in token_pattern.findall(formula):
            if token in functions:
                operators.append(token)
                expect_operand = True
            elif token == "(":
                operators.append(token)
                argument_counts.append(1)
                expect_operand = True
            elif token == ",":
                while operators[-1] != "(":
                    reduce_operator()
                argument_counts[-1] += 1
                expect_operand = True
            elif token == ")":
                while operators[-1] != "(":
                    reduce_operator()
                operators.pop()
                count = argument_counts.pop()
                if operators and operators[-1] in functions:
                    function = operators.pop()
                    arguments = nodes[-count:]
                    del nodes[-count:]
                    nodes.append(("call", function, arguments))
                expect_operand = False
            elif token == "-" and expect_operand:
                operators.append("neg")
            elif token in precedence:
                while (
                    operators
                    and operators[-1] in precedence
                    and precedence[operators[-1]] >= precedence[token]
                ):
                    reduce_operator()
                operators.append(token)
                expect_operand = True
            elif token[0].isdigit():
                nodes.append(("number", int(token)))
                expect_operand = False
            else:
                nodes.append(("reference", token))
                expect_operand = False

        while operators:
            reduce_operator()
        return nodes[0]

    def argument_nodes(arguments):
        for argument in arguments:
            if argument[0] != "range":
                yield argument
                continue

            first, last = argument[1], argument[2]
            col1, col2 = sorted((ord(first[0]), ord(last[0])))
            row1, row2 = sorted((int(first[1:]), int(last[1:])))
            for row in range(row1, row2 + 1):
                for col in range(col1, col2 + 1):
                    name = chr(col) + str(row)
                    if name in cells:
                        yield ("reference", name)

    values = {}
    active = set()

    def evaluate(name):
        tasks = [("evaluate", ("reference", name))]
        results = []

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "evaluate":
                node = task[1]
                node_kind = node[0]

                if node_kind == "number":
                    results.append(node[1])

                elif node_kind == "reference":
                    reference = node[1]
                    if reference in values:
                        results.append(values[reference])
                    elif reference not in cells:
                        results.append(0)
                    elif reference in active:
                        results.append("#CYCLE!")
                    else:
                        active.add(reference)
                        tasks.append(("finish_cell", reference))
                        content = cells[reference]
                        if content.startswith("="):
                            tasks.append(("evaluate", parse(content[1:])))
                        else:
                            results.append(int(content))

                elif node_kind == "neg":
                    tasks.append(("negate",))
                    tasks.append(("evaluate", node[1]))

                elif node_kind == "binary":
                    tasks.append(("left_done", node[1], node[3]))
                    tasks.append(("evaluate", node[2]))

                else:
                    function, arguments = node[1], node[2]
                    if function == "IF":
                        tasks.append(("choose", arguments[1], arguments[2]))
                        tasks.append(("evaluate", arguments[0]))
                    else:
                        initial = 0 if function == "SUM" else None
                        tasks.append((
                            "aggregate_next",
                            function,
                            iter(argument_nodes(arguments)),
                            initial,
                        ))

            elif kind == "finish_cell":
                reference = task[1]
                values[reference] = results[-1]
                active.remove(reference)

            elif kind == "negate":
                value = results.pop()
                results.append(value if isinstance(value, str) else -value)

            elif kind == "left_done":
                left = results.pop()
                if isinstance(left, str):
                    results.append(left)
                else:
                    tasks.append(("right_done", task[1], left))
                    tasks.append(("evaluate", task[2]))

            elif kind == "right_done":
                right = results.pop()
                if isinstance(right, str):
                    results.append(right)
                    continue

                op, left = task[1], task[2]
                if op == "+":
                    result = left + right
                elif op == "-":
                    result = left - right
                elif op == "*":
                    result = left * right
                elif op == "/":
                    if right == 0:
                        result = "#DIV/0!"
                    else:
                        quotient = abs(left) // abs(right)
                        result = -quotient if (left < 0) != (right < 0) else quotient
                elif op == "=":
                    result = left == right
                elif op == "<>":
                    result = left != right
                elif op == "<":
                    result = left < right
                elif op == "<=":
                    result = left <= right
                elif op == ">":
                    result = left > right
                else:
                    result = left >= right
                results.append(result)

            elif kind == "choose":
                condition = results.pop()
                if isinstance(condition, str):
                    results.append(condition)
                else:
                    tasks.append(("evaluate", task[1] if condition else task[2]))

            elif kind == "aggregate_next":
                function, iterator, accumulator = task[1:]
                node = next(iterator, None)
                if node is None:
                    results.append(0 if accumulator is None else accumulator)
                else:
                    tasks.append((
                        "aggregate_take", function, iterator, accumulator
                    ))
                    tasks.append(("evaluate", node))

            elif kind == "aggregate_take":
                value = results.pop()
                if isinstance(value, str):
                    results.append(value)
                    continue

                function, iterator, accumulator = task[1:]
                if accumulator is None:
                    accumulator = value
                elif function == "SUM":
                    accumulator += value
                elif function == "MIN":
                    accumulator = min(accumulator, value)
                else:
                    accumulator = max(accumulator, value)
                tasks.append((
                    "aggregate_next", function, iterator, accumulator
                ))

        return results.pop()

    for name in cells:
        if name not in values:
            evaluate(name)

    return {name: values[name] for name in cells}
