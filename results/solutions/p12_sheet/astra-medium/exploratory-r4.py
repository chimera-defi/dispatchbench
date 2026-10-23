def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    token_pattern = re.compile(
        r"\d+|[A-Z][1-9][0-9]?|SUM|MIN|MAX|IF|<>|<=|>=|[()+*/,:=<>-]"
    )
    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "neg": 3,
        ":": 4,
    }

    def parse(text):
        nodes = []
        operators = []
        argument_counts = []
        expect_operand = True

        def reduce_operator():
            op = operators.pop()
            if op == "neg":
                nodes.append(("neg", nodes.pop()))
            else:
                right = nodes.pop()
                left = nodes.pop()
                nodes.append((op, left, right))

        for match in token_pattern.finditer(text):
            token = match.group()

            if token[0].isdigit():
                nodes.append(("num", int(token)))
                expect_operand = False
            elif token in functions:
                operators.append(token)
                expect_operand = True
            elif token[0].isalpha():
                nodes.append(("ref", token))
                expect_operand = False
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
                    name = operators.pop()
                    args = nodes[-count:]
                    del nodes[-count:]
                    nodes.append(("call", name, args))
                expect_operand = False
            else:
                op = "neg" if token == "-" and expect_operand else token
                while (
                    operators
                    and operators[-1] in precedence
                    and (
                        precedence[operators[-1]] > precedence[op]
                        or (
                            precedence[operators[-1]] == precedence[op]
                            and op != "neg"
                        )
                    )
                ):
                    reduce_operator()
                operators.append(op)
                expect_operand = True

        while operators:
            reduce_operator()
        return nodes[0]

    def arguments_in_order(arguments):
        for argument in arguments:
            if argument[0] != ":":
                yield argument
                continue

            first = argument[1][1]
            second = argument[2][1]
            col1, col2 = sorted((ord(first[0]), ord(second[0])))
            row1, row2 = sorted((int(first[1:]), int(second[1:])))

            for row in range(row1, row2 + 1):
                for col in range(col1, col2 + 1):
                    name = chr(col) + str(row)
                    if name in cells:
                        yield ("ref", name)

    def apply_binary(op, left, right):
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                return "#DIV/0!"
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if op == "=":
            return left == right
        if op == "<>":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        return left >= right

    cache = {}
    active = set()

    for root in cells:
        if root in cache:
            continue

        tasks = [("cell", root)]
        values = []

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "cell":
                name = task[1]
                if name in cache:
                    values.append(cache[name])
                elif name not in cells:
                    values.append(0)
                elif name in active:
                    values.append("#CYCLE!")
                else:
                    content = cells[name].strip()
                    if not content.startswith("="):
                        value = int(content)
                        cache[name] = value
                        values.append(value)
                    else:
                        active.add(name)
                        tasks.append(("finish_cell", name))
                        tasks.append(("eval", parse(content[1:])))

            elif kind == "finish_cell":
                name = task[1]
                cache[name] = values[-1]
                active.remove(name)

            elif kind == "eval":
                node = task[1]
                op = node[0]

                if op == "num":
                    values.append(node[1])
                elif op == "ref":
                    tasks.append(("cell", node[1]))
                elif op == "neg":
                    tasks.append(("negate",))
                    tasks.append(("eval", node[1]))
                elif op == "call":
                    name, arguments = node[1], node[2]
                    if name == "IF":
                        tasks.append(("choose", arguments[1], arguments[2]))
                        tasks.append(("eval", arguments[0]))
                    else:
                        iterator = arguments_in_order(arguments)
                        tasks.append(("aggregate_next", name, iterator, None))
                else:
                    tasks.append(("binary_left", op, node[2]))
                    tasks.append(("eval", node[1]))

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
                if isinstance(right, str):
                    values.append(right)
                else:
                    values.append(apply_binary(task[1], task[2], right))

            elif kind == "choose":
                condition = values.pop()
                if isinstance(condition, str):
                    values.append(condition)
                else:
                    tasks.append(("eval", task[1] if condition else task[2]))

            elif kind == "aggregate_next":
                name, iterator, accumulated = task[1:]
                argument = next(iterator, None)
                if argument is None:
                    values.append(0 if accumulated is None else accumulated)
                else:
                    tasks.append(
                        ("aggregate_value", name, iterator, accumulated)
                    )
                    tasks.append(("eval", argument))

            elif kind == "aggregate_value":
                name, iterator, accumulated = task[1:]
                value = values.pop()
                if isinstance(value, str):
                    values.append(value)
                    continue

                if accumulated is None:
                    accumulated = value
                elif name == "SUM":
                    accumulated += value
                elif name == "MIN":
                    accumulated = min(accumulated, value)
                else:
                    accumulated = max(accumulated, value)

                tasks.append(("aggregate_next", name, iterator, accumulated))

    return {name: cache[name] for name in cells}
