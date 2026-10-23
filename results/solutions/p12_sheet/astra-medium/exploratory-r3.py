def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "neg": 3,
        ":": 4,
    }
    token_pattern = re.compile(
        r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[-+*/():,=<>]"
    )

    def parse(content):
        if not content.startswith("="):
            return int(content)

        tokens = token_pattern.findall(content[1:])
        operands = []
        operators = []
        argument_counts = []
        expect_operand = True

        def reduce_operator():
            op = operators.pop()
            if op == "neg":
                operands.append(("neg", operands.pop()))
            else:
                right = operands.pop()
                left = operands.pop()
                operands.append((op, left, right))

        for i, token in enumerate(tokens):
            if token[0].isdigit():
                operands.append(int(token))
                expect_operand = False
            elif token in functions:
                operators.append(token)
                expect_operand = True
            elif token[0].isalpha():
                operands.append(("ref", token))
                expect_operand = False
            elif token == "(":
                operators.append("(")
                is_call = i > 0 and tokens[i - 1] in functions
                argument_counts.append(1 if is_call else 0)
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
                if count:
                    function = operators.pop()
                    arguments = operands[-count:]
                    del operands[-count:]
                    operands.append((function, arguments))
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
        return operands[0]

    def argument_values(arguments):
        for argument in arguments:
            if isinstance(argument, tuple) and argument[0] == ":":
                first = argument[1][1]
                last = argument[2][1]
                left, right = sorted((ord(first[0]), ord(last[0])))
                top, bottom = sorted((int(first[1:]), int(last[1:])))
                for row in range(top, bottom + 1):
                    for column in range(left, right + 1):
                        name = chr(column) + str(row)
                        if name in cells:
                            yield ("ref", name)
            else:
                yield argument

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

    # State 1 means evaluation is in progress; state 2 means cached.
    state = {}
    cache = {}

    for root in cells:
        if state.get(root) == 2:
            continue

        tasks = [("cell", root)]
        value = 0

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "cell":
                name = task[1]
                if name not in cells:
                    value = 0
                elif state.get(name) == 2:
                    value = cache[name]
                elif state.get(name) == 1:
                    value = "#CYCLE!"
                else:
                    state[name] = 1
                    tasks.append(("finish_cell", name))
                    tasks.append(("eval", parse(cells[name])))

            elif kind == "finish_cell":
                name = task[1]
                cache[name] = value
                state[name] = 2

            elif kind == "eval":
                node = task[1]
                if isinstance(node, int):
                    value = node
                    continue

                op = node[0]
                if op == "ref":
                    tasks.append(("cell", node[1]))
                elif op == "neg":
                    tasks.append(("negate",))
                    tasks.append(("eval", node[1]))
                elif op == "IF":
                    condition, then_branch, else_branch = node[1]
                    tasks.append(("choose", then_branch, else_branch))
                    tasks.append(("eval", condition))
                elif op in ("SUM", "MIN", "MAX"):
                    iterator = argument_values(node[1])
                    tasks.append(("aggregate_next", op, iterator, None))
                else:
                    tasks.append(("binary_left", op, node[2]))
                    tasks.append(("eval", node[1]))

            elif kind == "negate":
                if not isinstance(value, str):
                    value = -value

            elif kind == "binary_left":
                if not isinstance(value, str):
                    tasks.append(("binary_right", task[1], value))
                    tasks.append(("eval", task[2]))

            elif kind == "binary_right":
                if not isinstance(value, str):
                    value = apply_binary(task[1], task[2], value)

            elif kind == "choose":
                if not isinstance(value, str):
                    branch = task[1] if value else task[2]
                    tasks.append(("eval", branch))

            elif kind == "aggregate_next":
                _, op, iterator, accumulated = task
                node = next(iterator, None)
                if node is None:
                    value = 0 if accumulated is None else accumulated
                else:
                    tasks.append(
                        ("aggregate_value", op, iterator, accumulated)
                    )
                    tasks.append(("eval", node))

            elif kind == "aggregate_value":
                if isinstance(value, str):
                    continue
                _, op, iterator, accumulated = task
                if accumulated is None:
                    accumulated = value
                elif op == "SUM":
                    accumulated += value
                elif op == "MIN":
                    accumulated = min(accumulated, value)
                else:
                    accumulated = max(accumulated, value)
                tasks.append(
                    ("aggregate_next", op, iterator, accumulated)
                )

    return {name: cache[name] for name in cells}
