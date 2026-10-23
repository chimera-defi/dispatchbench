def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    token_pattern = re.compile(
        r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[()+\-*/,:=<>]"
    )
    functions = {"SUM", "MIN", "MAX", "IF"}
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "NEG": 3,
        ":": 4,
    }

    def integer(text):
        text = text.strip()
        sign = 1
        if text[0] in "+-":
            if text[0] == "-":
                sign = -1
            text = text[1:]
        value = 0
        for i in range(0, len(text), 9):
            chunk = text[i:i + 9]
            value = value * (10 ** len(chunk)) + int(chunk)
        return sign * value

    def parse(formula):
        nodes = []
        operators = []
        argument_counts = []
        expecting_operand = True

        def reduce_operator():
            operator = operators.pop()
            if operator == "NEG":
                nodes.append(("neg", nodes.pop()))
            else:
                right = nodes.pop()
                left = nodes.pop()
                if operator == ":":
                    nodes.append(("range", left[1], right[1]))
                else:
                    nodes.append(("bin", operator, left, right))

        for match in token_pattern.finditer(formula):
            token = match.group()

            if token[0].isdigit():
                nodes.append(("num", integer(token)))
                expecting_operand = False
            elif token in functions:
                operators.append(token)
                expecting_operand = True
            elif token[0].isalpha():
                nodes.append(("ref", token))
                expecting_operand = False
            elif token == "(":
                operators.append(token)
                argument_counts.append(1)
                expecting_operand = True
            elif token == ",":
                while operators[-1] != "(":
                    reduce_operator()
                argument_counts[-1] += 1
                expecting_operand = True
            elif token == ")":
                while operators[-1] != "(":
                    reduce_operator()
                operators.pop()
                count = argument_counts.pop()
                if operators and operators[-1] in functions:
                    name = operators.pop()
                    arguments = tuple(nodes[-count:])
                    del nodes[-count:]
                    nodes.append(("call", name, arguments))
                expecting_operand = False
            elif token == "-" and expecting_operand:
                operators.append("NEG")
            else:
                while (
                    operators
                    and operators[-1] in precedence
                    and precedence[operators[-1]] >= precedence[token]
                ):
                    reduce_operator()
                operators.append(token)
                expecting_operand = True

        while operators:
            reduce_operator()
        return nodes[0]

    def argument_nodes(arguments):
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

    values = {}
    active = set()
    results = []
    tasks = []

    for root in cells:
        if root in values:
            continue

        tasks.append(("cell", root))

        while tasks:
            task = tasks.pop()
            kind = task[0]

            if kind == "cell":
                name = task[1]
                if name in values:
                    results.append(values[name])
                elif name not in cells:
                    results.append(0)
                elif name in active:
                    results.append("#CYCLE!")
                else:
                    active.add(name)
                    tasks.append(("finish_cell", name))
                    content = cells[name].strip()
                    if content.startswith("="):
                        tasks.append(("eval", parse(content[1:])))
                    else:
                        results.append(integer(content))

            elif kind == "finish_cell":
                name = task[1]
                values[name] = results[-1]
                active.remove(name)

            elif kind == "eval":
                node = task[1]
                node_kind = node[0]

                if node_kind == "num":
                    results.append(node[1])
                elif node_kind == "ref":
                    tasks.append(("cell", node[1]))
                elif node_kind == "neg":
                    tasks.append(("negate",))
                    tasks.append(("eval", node[1]))
                elif node_kind == "bin":
                    tasks.append(("left_done", node[1], node[3]))
                    tasks.append(("eval", node[2]))
                elif node_kind == "call":
                    name, arguments = node[1], node[2]
                    if name == "IF":
                        tasks.append(("choose", arguments[1], arguments[2]))
                        tasks.append(("eval", arguments[0]))
                    else:
                        initial = 0 if name == "SUM" else None
                        tasks.append((
                            "next_argument",
                            name,
                            argument_nodes(arguments),
                            initial,
                        ))

            elif kind == "negate":
                value = results.pop()
                results.append(value if isinstance(value, str) else -value)

            elif kind == "left_done":
                left = results.pop()
                if isinstance(left, str):
                    results.append(left)
                else:
                    tasks.append(("right_done", task[1], left))
                    tasks.append(("eval", task[2]))

            elif kind == "right_done":
                right = results.pop()
                operator, left = task[1], task[2]

                if isinstance(right, str):
                    results.append(right)
                    continue

                if operator == "+":
                    value = left + right
                elif operator == "-":
                    value = left - right
                elif operator == "*":
                    value = left * right
                elif operator == "/":
                    if right == 0:
                        value = "#DIV/0!"
                    else:
                        value = abs(left) // abs(right)
                        if (left < 0) != (right < 0):
                            value = -value
                elif operator == "=":
                    value = left == right
                elif operator == "<>":
                    value = left != right
                elif operator == "<":
                    value = left < right
                elif operator == "<=":
                    value = left <= right
                elif operator == ">":
                    value = left > right
                else:
                    value = left >= right

                results.append(value)

            elif kind == "choose":
                condition = results.pop()
                if isinstance(condition, str):
                    results.append(condition)
                else:
                    tasks.append(("eval", task[1] if condition else task[2]))

            elif kind == "next_argument":
                name, iterator, accumulator = task[1:]
                node = next(iterator, None)
                if node is None:
                    results.append(0 if accumulator is None else accumulator)
                else:
                    tasks.append(("argument_done", name, iterator, accumulator))
                    tasks.append(("eval", node))

            elif kind == "argument_done":
                value = results.pop()
                if isinstance(value, str):
                    results.append(value)
                    continue

                name, iterator, accumulator = task[1:]
                if name == "SUM":
                    accumulator += value
                elif accumulator is None:
                    accumulator = value
                elif name == "MIN":
                    accumulator = min(accumulator, value)
                else:
                    accumulator = max(accumulator, value)

                tasks.append(("next_argument", name, iterator, accumulator))

        results.pop()

    return {name: values[name] for name in cells}
