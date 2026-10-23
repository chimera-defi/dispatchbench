def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    token_pattern = re.compile(r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[()+*/,:=<>-]")
    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "neg": 3,
        ":": 4,
    }
    div_error = "#DIV/0!"
    cycle_error = "#CYCLE!"

    def parse(content):
        content = content.strip()
        if not content.startswith("="):
            return ("number", int(content))

        nodes = []
        operators = []
        frames = []
        expect_operand = True

        def reduce_operator():
            op = operators.pop()
            if op == "neg":
                nodes.append(("neg", nodes.pop()))
            else:
                right = nodes.pop()
                left = nodes.pop()
                nodes.append((op, left, right))

        for token in token_pattern.findall(content[1:]):
            if token[0].isdigit():
                nodes.append(("number", int(token)))
                expect_operand = False
            elif token in functions:
                operators.append(token)
                expect_operand = True
            elif token[0].isalpha():
                nodes.append(("reference", token))
                expect_operand = False
            elif token == "(":
                is_call = bool(operators and operators[-1] in functions)
                frames.append([is_call, 1])
                operators.append("(")
                expect_operand = True
            elif token == ",":
                while operators[-1] != "(":
                    reduce_operator()
                frames[-1][1] += 1
                expect_operand = True
            elif token == ")":
                while operators[-1] != "(":
                    reduce_operator()
                operators.pop()
                is_call, count = frames.pop()
                if is_call:
                    function = operators.pop()
                    arguments = tuple(nodes[-count:])
                    del nodes[-count:]
                    nodes.append((function, arguments))
                expect_operand = False
            elif token == "-" and expect_operand:
                operators.append("neg")
            else:
                while (
                    operators
                    and operators[-1] in precedence
                    and precedence[operators[-1]] >= precedence[token]
                ):
                    reduce_operator()
                operators.append(token)
                expect_operand = True

        while operators:
            reduce_operator()
        return nodes[0]

    expressions = {name: parse(content) for name, content in cells.items()}
    memo = {}
    active = set()

    def expanded_arguments(arguments):
        for argument in arguments:
            if argument[0] != ":":
                yield argument
                continue

            first = argument[1][1]
            last = argument[2][1]
            c1, c2 = sorted((ord(first[0]), ord(last[0])))
            r1, r2 = sorted((int(first[1:]), int(last[1:])))
            for row in range(r1, r2 + 1):
                for column in range(c1, c2 + 1):
                    name = chr(column) + str(row)
                    if name in expressions:
                        yield ("reference", name)

    def apply_binary(op, left, right):
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                return div_error
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

    for root in cells:
        if root in memo:
            continue

        tasks = [("cell", root)]
        values = []

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "cell":
                name = task[1]
                if name in memo:
                    values.append(memo[name])
                elif name not in expressions:
                    values.append(0)
                elif name in active:
                    values.append(cycle_error)
                else:
                    active.add(name)
                    tasks.append(("finish_cell", name))
                    tasks.append(("evaluate", expressions[name]))

            elif kind == "finish_cell":
                name = task[1]
                memo[name] = values[-1]
                active.remove(name)

            elif kind == "evaluate":
                node = task[1]
                op = node[0]

                if op == "number":
                    values.append(node[1])
                elif op == "reference":
                    tasks.append(("cell", node[1]))
                elif op == "neg":
                    tasks.append(("negate",))
                    tasks.append(("evaluate", node[1]))
                elif op == "IF":
                    condition, then_branch, else_branch = node[1]
                    tasks.append(("choose", then_branch, else_branch))
                    tasks.append(("evaluate", condition))
                elif op in ("SUM", "MIN", "MAX"):
                    iterator = expanded_arguments(node[1])
                    initial = 0 if op == "SUM" else None
                    tasks.append(("aggregate_next", op, iterator, initial))
                else:
                    tasks.append(("binary_left", op, node[2]))
                    tasks.append(("evaluate", node[1]))

            elif kind == "negate":
                value = values.pop()
                values.append(value if isinstance(value, str) else -value)

            elif kind == "binary_left":
                left = values.pop()
                if isinstance(left, str):
                    values.append(left)
                else:
                    tasks.append(("binary_right", task[1], left))
                    tasks.append(("evaluate", task[2]))

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
                    branch = task[1] if condition else task[2]
                    tasks.append(("evaluate", branch))

            elif kind == "aggregate_next":
                _, op, iterator, accumulator = task
                argument = next(iterator, None)
                if argument is None:
                    values.append(0 if accumulator is None else accumulator)
                else:
                    tasks.append(("aggregate_value", op, iterator, accumulator))
                    tasks.append(("evaluate", argument))

            elif kind == "aggregate_value":
                _, op, iterator, accumulator = task
                value = values.pop()
                if isinstance(value, str):
                    values.append(value)
                else:
                    if accumulator is None:
                        accumulator = value
                    elif op == "SUM":
                        accumulator += value
                    elif op == "MIN":
                        accumulator = min(accumulator, value)
                    else:
                        accumulator = max(accumulator, value)
                    tasks.append(("aggregate_next", op, iterator, accumulator))

    return {name: memo[name] for name in cells}
