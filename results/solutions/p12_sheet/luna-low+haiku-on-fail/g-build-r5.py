def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    tokens_re = re.compile(
        r"\s*(?:(\d+)|([A-Z]\d{1,2})|(SUM|MIN|MAX|IF)|"
        r"(<>|<=|>=|[()+\-*/,:=<>]))"
    )

    parsed = {}

    def tokenize(text):
        result = []
        pos = 0
        while pos < len(text):
            match = tokens_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            number, cell, function, operator = match.groups()
            if number is not None:
                result.append(("num", int(number)))
            elif cell is not None:
                result.append(("cell", cell))
            elif function is not None:
                result.append(("func", function))
            else:
                result.append((operator, operator))
            pos = match.end()
        result.append(("eof", None))
        return result

    def parse_formula(text):
        tokens = tokenize(text)
        index = 0

        def peek():
            return tokens[index][0]

        def take(kind=None):
            nonlocal index
            token = tokens[index]
            if kind is not None and token[0] != kind:
                raise ValueError("Invalid formula")
            index += 1
            return token

        def atom():
            kind, value = tokens[index]
            if kind == "num":
                take()
                return ("num", value)
            if kind == "cell":
                take()
                return ("cell", value)
            if kind == "(":
                take()
                node = expression()
                take(")")
                return node
            if kind == "func":
                function = take()[1]
                take("(")
                if function == "IF":
                    left = expression()
                    op = peek()
                    if op not in ("=", "<>", "<", "<=", ">", ">="):
                        raise ValueError("Invalid formula")
                    take()
                    right = expression()
                    take(",")
                    then_node = expression()
                    take(",")
                    else_node = expression()
                    take(")")
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    if peek() == "cell" and tokens[index + 1][0] == ":":
                        start = take("cell")[1]
                        take(":")
                        end = take("cell")[1]
                        args.append(("range", start, end))
                    else:
                        args.append(expression())
                    if peek() != ",":
                        break
                    take(",")
                take(")")
                if not args:
                    raise ValueError("Invalid formula")
                return ("call", function, args)
            raise ValueError("Invalid formula")

        def unary():
            if peek() == "-":
                take("-")
                return ("neg", unary())
            return atom()

        def product():
            node = unary()
            while peek() in ("*", "/"):
                op = take()[0]
                node = ("bin", op, node, unary())
            return node

        def expression():
            node = product()
            while peek() in ("+", "-"):
                op = take()[0]
                node = ("bin", op, node, product())
            return node

        root = expression()
        take("eof")
        return root

    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = parse_formula(content[1:])
        else:
            parsed[name] = int(content)

    values = {}
    active = set()
    frames = []

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return "#CYCLE!"
        active.add(name)
        frames.append([name, iter_eval(parsed[name])])
        return None

    def iter_eval(node):
        # Evaluation uses explicit frames so long cell-reference chains do not
        # consume Python's recursion limit.
        stack = [["node", node]]
        result = None

        while stack:
            frame = stack[-1]
            if frame[0] == "node":
                current = frame[1]
                kind = current[0]

                if kind == "num":
                    stack.pop()
                    result = current[1]
                elif kind == "cell":
                    stack.pop()
                    result = cell_value(current[1])
                    if result is None:
                        return ("pending", current[1])
                elif kind == "neg":
                    stack[-1] = ["neg_wait", current[1]]
                    stack.append(["node", current[1]])
                elif kind == "bin":
                    stack[-1] = ["bin_left", current[1], current[2], current[3]]
                    stack.append(["node", current[2]])
                elif kind == "if":
                    stack[-1] = ["if_left", current[1], current[2], current[3],
                                 current[4], current[5]]
                    stack.append(["node", current[2]])
                elif kind == "call":
                    stack[-1] = ["call", current[1], current[2], 0, []]
                elif kind == "range":
                    stack.pop()
                    result = 0
                else:
                    raise ValueError("Invalid formula")
                continue

            if frame[0] == "neg_wait":
                stack.pop()
                result = result if isinstance(result, str) else -result
            elif frame[0] == "bin_left":
                _, op, left_node, right_node = frame
                left_value = result
                if isinstance(left_value, str):
                    stack.pop()
                    result = left_value
                else:
                    stack[-1] = ["bin_right", op, left_value]
                    stack.append(["node", right_node])
            elif frame[0] == "bin_right":
                _, op, left_value = frame
                right_value = result
                stack.pop()
                if isinstance(right_value, str):
                    result = right_value
                elif op == "+":
                    result = left_value + right_value
                elif op == "-":
                    result = left_value - right_value
                elif op == "*":
                    result = left_value * right_value
                elif right_value == 0:
                    result = "#DIV/0!"
                else:
                    quotient = abs(left_value) // abs(right_value)
                    result = -quotient if (left_value < 0) != (right_value < 0) else quotient
            elif frame[0] == "if_left":
                _, op, left_node, right_node, then_node, else_node = frame
                left_value = result
                if isinstance(left_value, str):
                    stack.pop()
                    result = left_value
                else:
                    stack[-1] = ["if_right", op, left_value, right_node,
                                 then_node, else_node]
                    stack.append(["node", right_node])
            elif frame[0] == "if_right":
                _, op, left_value, _, then_node, else_node = frame
                right_value = result
                if isinstance(right_value, str):
                    stack.pop()
                    result = right_value
                else:
                    comparisons = {
                        "=": left_value == right_value,
                        "<>": left_value != right_value,
                        "<": left_value < right_value,
                        "<=": left_value <= right_value,
                        ">": left_value > right_value,
                        ">=": left_value >= right_value,
                    }
                    stack.pop()
                    stack.append(["node", then_node if comparisons[op] else else_node])
            elif frame[0] == "call":
                _, function, args, arg_index, collected = frame
                if arg_index >= len(args):
                    stack.pop()
                    if function == "SUM":
                        result = sum(collected)
                    elif not collected:
                        result = 0
                    elif function == "MIN":
                        result = min(collected)
                    else:
                        result = max(collected)
                    continue

                arg = args[arg_index]
                if arg[0] == "range":
                    start_col, start_row = ord(arg[1][0]) - 65, int(arg[1][1:])
                    end_col, end_row = ord(arg[2][0]) - 65, int(arg[2][1:])
                    min_col, max_col = sorted((start_col, end_col))
                    min_row, max_row = sorted((start_row, end_row))
                    names = [
                        chr(col + 65) + str(row)
                        for row in range(min_row, max_row + 1)
                        for col in range(min_col, max_col + 1)
                        if chr(col + 65) + str(row) in cells
                    ]
                    stack[-1] = ["range_eval", function, args, arg_index,
                                 collected, names, 0]
                else:
                    stack[-1] = ["arg_wait", function, args, arg_index, collected]
                    stack.append(["node", arg])
            elif frame[0] == "arg_wait":
                _, function, args, arg_index, collected = frame
                if isinstance(result, str):
                    stack.pop()
                else:
                    collected.append(result)
                    stack[-1] = ["call", function, args, arg_index + 1, collected]
            elif frame[0] == "range_eval":
                _, function, args, arg_index, collected, names, name_index = frame
                if name_index >= len(names):
                    stack[-1] = ["call", function, args, arg_index + 1, collected]
                    continue
                name = names[name_index]
                stack[-1] = ["range_wait", function, args, arg_index,
                             collected, names, name_index]
                stack.append(["node", ("cell", name)])
            elif frame[0] == "range_wait":
                _, function, args, arg_index, collected, names, name_index = frame
                if isinstance(result, str):
                    stack.pop()
                else:
                    collected.append(result)
                    stack[-1] = ["range_eval", function, args, arg_index,
                                 collected, names, name_index + 1]
            else:
                raise ValueError("Invalid evaluator state")

        return result

    def evaluate_cell(name):
        if name in values:
            return values[name]
        if name in active:
            return "#CYCLE!"
        active.add(name)
        if isinstance(parsed[name], int):
            value = parsed[name]
        else:
            value = iter_eval(parsed[name])
        active.remove(name)
        values[name] = value
        return value

    # Evaluate cells through an explicit dependency stack to support chains
    # longer than Python's recursion limit.
    for initial in cells:
        if initial in values:
            continue

        work = [[initial, None]]
        active.add(initial)
        while work:
            name, evaluator = work[-1]
            if evaluator is None:
                if isinstance(parsed[name], int):
                    values[name] = parsed[name]
                    active.remove(name)
                    work.pop()
                    continue
                evaluator = iter_eval(parsed[name])
                work[-1][1] = evaluator

            outcome = next(evaluator)
            if outcome[0] == "done":
                values[name] = outcome[1]
                active.remove(name)
                work.pop()
            elif outcome[0] == "ref":
                ref = outcome[1]
                if ref not in cells:
                    evaluator.send(0)
                elif ref in values:
                    evaluator.send(values[ref])
                elif ref in active:
                    evaluator.send("#CYCLE!")
                else:
                    active.add(ref)
                    work.append([ref, None])

    return {name: values[name] for name in cells}
