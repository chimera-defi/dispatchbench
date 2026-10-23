def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 1, "<>": 1, "<": 1, "<=": 1, ">": 1, ">=": 1,
        "+": 2, "-": 2,
        "*": 3, "/": 3,
        "neg": 4,
        ":": 5,
    }

    def parse(content):
        if not content.lstrip().startswith("="):
            return ("num", int(content))

        formula = content.lstrip()[1:]
        tokens = re.findall(
            r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[^\s]", formula
        )
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

        for token in tokens:
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
                    function = operators.pop()
                    arguments = tuple(nodes[-count:])
                    del nodes[-count:]
                    nodes.append((function, arguments))
                expect_operand = False
            else:
                op = "neg" if token == "-" and expect_operand else token
                while operators and operators[-1] in precedence:
                    top = operators[-1]
                    if precedence[top] < precedence[op]:
                        break
                    if precedence[top] == precedence[op] and op == "neg":
                        break
                    reduce_operator()
                operators.append(op)
                expect_operand = True

        while operators:
            reduce_operator()
        return nodes[0]

    trees = {name: parse(content) for name, content in cells.items()}
    state = {}  # 1: evaluating, 2: finished
    results = {}

    def argument_nodes(arguments):
        for argument in arguments:
            if argument[0] != ":":
                yield argument
                continue

            first = argument[1][1]
            last = argument[2][1]
            col1, col2 = sorted((ord(first[0]), ord(last[0])))
            row1, row2 = sorted((int(first[1:]), int(last[1:])))

            for row in range(row1, row2 + 1):
                for column in range(col1, col2 + 1):
                    name = chr(column) + str(row)
                    if name in cells:
                        yield ("ref", name)

    def calculate(op, left, right):
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
            return int(left == right)
        if op == "<>":
            return int(left != right)
        if op == "<":
            return int(left < right)
        if op == "<=":
            return int(left <= right)
        if op == ">":
            return int(left > right)
        return int(left >= right)

    for root in cells:
        if state.get(root) == 2:
            continue

        tasks = [("cell", root)]
        values = []

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "cell":
                name = task[1]
                if name not in cells:
                    values.append(0)
                elif state.get(name) == 2:
                    values.append(results[name])
                elif state.get(name) == 1:
                    values.append("#CYCLE!")
                else:
                    state[name] = 1
                    tasks.append(("finish", name))
                    tasks.append(("eval", trees[name]))

            elif kind == "finish":
                name = task[1]
                results[name] = values[-1]
                state[name] = 2

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
                elif op == "IF":
                    condition, then_branch, else_branch = node[1]
                    tasks.append(("choose", then_branch, else_branch))
                    tasks.append(("eval", condition))
                elif op in ("SUM", "MIN", "MAX"):
                    iterator = argument_nodes(node[1])
                    initial = 0 if op == "SUM" else None
                    tasks.append(("aggregate", op, iterator, initial))
                else:
                    tasks.append(("left_done", op, node[2]))
                    tasks.append(("eval", node[1]))

            elif kind == "negate":
                value = values.pop()
                values.append(value if isinstance(value, str) else -value)

            elif kind == "left_done":
                left = values.pop()
                if isinstance(left, str):
                    values.append(left)
                else:
                    tasks.append(("right_done", task[1], left))
                    tasks.append(("eval", task[2]))

            elif kind == "right_done":
                right = values.pop()
                if isinstance(right, str):
                    values.append(right)
                else:
                    values.append(calculate(task[1], task[2], right))

            elif kind == "choose":
                condition = values.pop()
                if isinstance(condition, str):
                    values.append(condition)
                else:
                    branch = task[1] if condition else task[2]
                    tasks.append(("eval", branch))

            elif kind == "aggregate":
                _, op, iterator, accumulated = task
                node = next(iterator, None)
                if node is None:
                    values.append(0 if accumulated is None else accumulated)
                else:
                    tasks.append(("aggregate_done", op, iterator, accumulated))
                    tasks.append(("eval", node))

            elif kind == "aggregate_done":
                _, op, iterator, accumulated = task
                value = values.pop()
                if isinstance(value, str):
                    values.append(value)
                    continue

                if accumulated is None:
                    accumulated = value
                elif op == "SUM":
                    accumulated += value
                elif op == "MIN":
                    accumulated = min(accumulated, value)
                else:
                    accumulated = max(accumulated, value)

                tasks.append(("aggregate", op, iterator, accumulated))

    return {name: results[name] for name in cells}
