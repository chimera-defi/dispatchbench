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
        "neg": 3,
        ":": 4,
    }

    def parse(content):
        if not content.startswith("="):
            return ("int", int(content))

        nodes = []
        operators = []
        argument_counts = []
        expecting_operand = True

        def reduce_operator():
            operator = operators.pop()
            if operator == "neg":
                nodes.append(("neg", nodes.pop()))
            else:
                right = nodes.pop()
                left = nodes.pop()
                if operator == ":":
                    nodes.append(("range", left[1], right[1]))
                else:
                    nodes.append(("binary", operator, left, right))

        for token in token_pattern.findall(content[1:]):
            if token[0].isdigit():
                nodes.append(("int", int(token)))
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
                    function = operators.pop()
                    arguments = tuple(nodes[-count:])
                    del nodes[-count:]
                    nodes.append(("call", function, arguments))
                expecting_operand = False
            elif token == "-" and expecting_operand:
                operators.append("neg")
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

    def expanded_arguments(arguments):
        for argument in arguments:
            if argument[0] != "range":
                yield argument
                continue

            first, second = argument[1], argument[2]
            first_col, second_col = ord(first[0]), ord(second[0])
            first_row, second_row = int(first[1:]), int(second[1:])

            for row in range(min(first_row, second_row),
                             max(first_row, second_row) + 1):
                for column in range(min(first_col, second_col),
                                    max(first_col, second_col) + 1):
                    name = chr(column) + str(row)
                    if name in cells:
                        yield ("ref", name)

    values = {}
    active = set()

    def evaluate(start):
        tasks = [("cell", start)]
        result = 0

        while tasks:
            task = tasks.pop()
            action = task[0]

            if action == "cell":
                name = task[1]
                if name not in cells:
                    result = 0
                elif name in values:
                    result = values[name]
                elif name in active:
                    result = "#CYCLE!"
                else:
                    active.add(name)
                    tasks.append(("save", name))
                    tasks.append(("eval", parse(cells[name])))

            elif action == "save":
                name = task[1]
                values[name] = result
                active.remove(name)

            elif action == "eval":
                node = task[1]
                kind = node[0]

                if kind == "int":
                    result = node[1]
                elif kind == "ref":
                    tasks.append(("cell", node[1]))
                elif kind == "neg":
                    tasks.append(("negate",))
                    tasks.append(("eval", node[1]))
                elif kind == "binary":
                    tasks.append(("binary_left", node[1], node[3]))
                    tasks.append(("eval", node[2]))
                elif kind == "call":
                    function, arguments = node[1], node[2]
                    if function == "IF":
                        tasks.append(("choose", arguments[1], arguments[2]))
                        tasks.append(("eval", arguments[0]))
                    else:
                        iterator = expanded_arguments(arguments)
                        initial = 0 if function == "SUM" else None
                        tasks.append(("aggregate_next", function,
                                      iterator, initial))

            elif action == "negate":
                if not isinstance(result, str):
                    result = -result

            elif action == "binary_left":
                if not isinstance(result, str):
                    tasks.append(("binary_right", task[1], result))
                    tasks.append(("eval", task[2]))

            elif action == "binary_right":
                if isinstance(result, str):
                    continue

                operator, left = task[1], task[2]
                right = result

                if operator == "+":
                    result = left + right
                elif operator == "-":
                    result = left - right
                elif operator == "*":
                    result = left * right
                elif operator == "/":
                    if right == 0:
                        result = "#DIV/0!"
                    else:
                        quotient = abs(left) // abs(right)
                        result = -quotient if (left < 0) != (right < 0) else quotient
                elif operator == "=":
                    result = left == right
                elif operator == "<>":
                    result = left != right
                elif operator == "<":
                    result = left < right
                elif operator == "<=":
                    result = left <= right
                elif operator == ">":
                    result = left > right
                elif operator == ">=":
                    result = left >= right

            elif action == "choose":
                if not isinstance(result, str):
                    branch = task[1] if result else task[2]
                    tasks.append(("eval", branch))

            elif action == "aggregate_next":
                function, iterator, accumulator = task[1:]
                argument = next(iterator, None)
                if argument is None:
                    result = 0 if accumulator is None else accumulator
                else:
                    tasks.append(("aggregate_value", function,
                                  iterator, accumulator))
                    tasks.append(("eval", argument))

            elif action == "aggregate_value":
                if isinstance(result, str):
                    continue

                function, iterator, accumulator = task[1:]
                if function == "SUM":
                    accumulator += result
                elif accumulator is None:
                    accumulator = result
                elif function == "MIN":
                    accumulator = min(accumulator, result)
                else:
                    accumulator = max(accumulator, result)

                tasks.append(("aggregate_next", function,
                              iterator, accumulator))

        return result

    for name in cells:
        if name not in values:
            evaluate(name)

    return {name: values[name] for name in cells}
