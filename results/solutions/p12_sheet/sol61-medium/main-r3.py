import re


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    token_pattern = re.compile(
        r"[0-9]+|[A-Z]+[0-9]*|<>|<=|>=|[+\-*/():,=<>]"
    )
    precedence = {
        "=": 0, "<>": 0, "<": 0, "<=": 0, ">": 0, ">=": 0,
        "+": 1, "-": 1,
        "*": 2, "/": 2,
        "neg": 3,
        ":": 4,
    }

    def parse(text):
        tokens = token_pattern.findall(text)
        nodes = []
        operators = []
        parentheses = []

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
                nodes.append(("bin", op, left, right))

        expecting_operand = True
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token in ("SUM", "MIN", "MAX", "IF"):
                operators.append("(")
                parentheses.append([token, 0])
                expecting_operand = True
                i += 2  # Consume the function name and opening parenthesis.
                continue

            if token == "(":
                operators.append("(")
                parentheses.append([None, 0])
                expecting_operand = True

            elif token == ")":
                while operators[-1] != "(":
                    reduce_operator()
                operators.pop()
                function, commas = parentheses.pop()
                if function is not None:
                    count = commas + 1
                    arguments = nodes[-count:]
                    del nodes[-count:]
                    nodes.append(("call", function, arguments))
                expecting_operand = False

            elif token == ",":
                while operators[-1] != "(":
                    reduce_operator()
                parentheses[-1][1] += 1
                expecting_operand = True

            elif token in precedence:
                op = "neg" if token == "-" and expecting_operand else token
                while operators and operators[-1] != "(":
                    previous = operators[-1]
                    if precedence[previous] < precedence[op]:
                        break
                    if op == "neg" and precedence[previous] == precedence[op]:
                        break
                    reduce_operator()
                operators.append(op)
                expecting_operand = True

            else:
                if token[0].isdigit():
                    nodes.append(("num", int(token)))
                else:
                    nodes.append(("ref", token))
                expecting_operand = False

            i += 1

        while operators:
            reduce_operator()
        return nodes[0]

    def argument_values(arguments):
        for argument in arguments:
            if argument[0] != "range":
                yield argument
                continue

            first, last = argument[1], argument[2]
            left, right = sorted((ord(first[0]), ord(last[0])))
            top, bottom = sorted((int(first[1:]), int(last[1:])))
            for row in range(top, bottom + 1):
                for column in range(left, right + 1):
                    name = chr(column) + str(row)
                    if name in cells:
                        yield ("ref", name)

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
                    active.add(name)
                    contents = cells[name].strip()
                    node = (
                        parse(contents[1:])
                        if contents.startswith("=")
                        else ("num", int(contents))
                    )
                    tasks.append(("save", name))
                    tasks.append(("eval", node))

            elif kind == "save":
                name = task[1]
                cache[name] = values[-1]
                active.remove(name)

            elif kind == "eval":
                node = task[1]
                node_kind = node[0]

                if node_kind == "num":
                    values.append(node[1])
                elif node_kind == "ref":
                    tasks.append(("cell", node[1]))
                elif node_kind == "neg":
                    tasks.append(("neg",))
                    tasks.append(("eval", node[1]))
                elif node_kind == "bin":
                    tasks.append(("left", node[1], node[3]))
                    tasks.append(("eval", node[2]))
                elif node_kind == "call":
                    function, arguments = node[1], node[2]
                    if function == "IF":
                        tasks.append(("choose", arguments[1], arguments[2]))
                        tasks.append(("eval", arguments[0]))
                    else:
                        initial = 0 if function == "SUM" else None
                        tasks.append((
                            "aggregate", function,
                            argument_values(arguments), initial
                        ))

            elif kind == "neg":
                value = values.pop()
                values.append(value if isinstance(value, str) else -value)

            elif kind == "left":
                left = values.pop()
                if isinstance(left, str):
                    values.append(left)
                else:
                    tasks.append(("binary", task[1], left))
                    tasks.append(("eval", task[2]))

            elif kind == "binary":
                right = values.pop()
                op, left = task[1], task[2]

                if isinstance(right, str):
                    result = right
                elif op == "+":
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

                values.append(result)

            elif kind == "choose":
                condition = values.pop()
                if isinstance(condition, str):
                    values.append(condition)
                else:
                    tasks.append(("eval", task[1] if condition else task[2]))

            elif kind == "aggregate":
                function, iterator, accumulated = task[1:]
                argument = next(iterator, None)
                if argument is None:
                    values.append(0 if accumulated is None else accumulated)
                else:
                    tasks.append(("aggregate_value", function, iterator, accumulated))
                    tasks.append(("eval", argument))

            elif kind == "aggregate_value":
                value = values.pop()
                if isinstance(value, str):
                    values.append(value)
                    continue

                function, iterator, accumulated = task[1:]
                if function == "SUM":
                    accumulated += value
                elif accumulated is None:
                    accumulated = value
                elif function == "MIN":
                    accumulated = min(accumulated, value)
                else:
                    accumulated = max(accumulated, value)

                tasks.append(("aggregate", function, iterator, accumulated))

    return {name: cache[name] for name in cells}
