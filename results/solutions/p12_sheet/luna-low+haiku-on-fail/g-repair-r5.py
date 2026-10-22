def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    token_re = re.compile(
        r"\s*(?:(\d+)|([A-Z]\d{1,2})|(SUM|MIN|MAX|IF)|"
        r"(<>|<=|>=|[()+\-*/,:=<>]))"
    )
    comparisons = {
        "=": lambda a, b: a == b,
        "<>": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }

    def tokenize(text):
        text = text.strip()
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            number, cell, function, operator = match.groups()
            if number is not None:
                tokens.append(("num", int(number)))
            elif cell is not None:
                tokens.append(("cell", cell))
            elif function is not None:
                tokens.append(("func", function))
            else:
                tokens.append((operator, operator))
            pos = match.end()
        tokens.append(("eof", None))
        return tokens

    def parse(text):
        tokens = tokenize(text)
        pos = 0

        def peek():
            return tokens[pos][0]

        def take(kind=None):
            nonlocal pos
            token = tokens[pos]
            if kind is not None and token[0] != kind:
                raise ValueError("Invalid formula")
            pos += 1
            return token

        def expression():
            node = product()
            while peek() in ("+", "-"):
                op = take()[0]
                node = ("bin", op, node, product())
            return node

        def product():
            node = unary()
            while peek() in ("*", "/"):
                op = take()[0]
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() == "-":
                take()
                return ("neg", unary())
            return atom()

        def atom():
            kind, value = tokens[pos]
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
                take()
                take("(")
                if value == "IF":
                    left = expression()
                    if peek() not in comparisons:
                        raise ValueError("Invalid formula")
                    op = take()[0]
                    right = expression()
                    take(",")
                    then_node = expression()
                    take(",")
                    else_node = expression()
                    take(")")
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    if peek() == "cell" and tokens[pos + 1][0] == ":":
                        start = take()[1]
                        take(":")
                        end = take("cell")[1]
                        args.append(("range", start, end))
                    else:
                        args.append(expression())
                    if peek() != ",":
                        break
                    take()
                take(")")
                return ("call", value, args)
            raise ValueError("Invalid formula")

        root = expression()
        take("eof")
        return root

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = parse(content[1:])
        else:
            parsed[name] = ("num", int(content.strip()))

    # Existing cells sorted row-major (top row first, left to right).
    positions = sorted(
        (int(name[1:]), ord(name[0]) - 65, name) for name in cells
    )

    def range_names(start, end):
        c1, r1 = ord(start[0]) - 65, int(start[1:])
        c2, r2 = ord(end[0]) - 65, int(end[1:])
        lo_c, hi_c = sorted((c1, c2))
        lo_r, hi_r = sorted((r1, r2))
        return [
            name
            for row, col, name in positions
            if lo_r <= row <= hi_r and lo_c <= col <= hi_c
        ]

    def binop(op, left, right):
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if right == 0:
            return "#DIV/0!"
        quotient = abs(left) // abs(right)
        return quotient if (left < 0) == (right < 0) else -quotient

    def run(node):
        # Generator: yields a cell name to request its value, receives the
        # value back via send(). Cell-to-cell dependencies are handled by the
        # driver below, so Python recursion only follows formula nesting.
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "cell":
            if node[1] not in cells:
                return 0
            return (yield node[1])
        if kind == "neg":
            value = yield from run(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            left = yield from run(node[2])
            if isinstance(left, str):
                return left
            right = yield from run(node[3])
            if isinstance(right, str):
                return right
            return binop(node[1], left, right)
        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = yield from run(left_node)
            if isinstance(left, str):
                return left
            right = yield from run(right_node)
            if isinstance(right, str):
                return right
            chosen = then_node if comparisons[op](left, right) else else_node
            return (yield from run(chosen))

        _, function, args = node
        collected = []
        for arg in args:
            if arg[0] == "range":
                for name in range_names(arg[1], arg[2]):
                    value = yield name
                    if isinstance(value, str):
                        return value
                    collected.append(value)
            else:
                value = yield from run(arg)
                if isinstance(value, str):
                    return value
                collected.append(value)

        if function == "SUM":
            return sum(collected)
        if not collected:
            return 0
        return min(collected) if function == "MIN" else max(collected)

    values = {}
    for start in cells:
        if start in values:
            continue
        in_progress = {start}
        stack = [(start, run(parsed[start]))]
        send = None
        while stack:
            name, gen = stack[-1]
            try:
                ref = gen.send(send)
            except StopIteration as done:
                values[name] = done.value
                in_progress.discard(name)
                stack.pop()
                send = done.value
                continue
            if ref in values:
                send = values[ref]
            elif ref in in_progress:
                send = "#CYCLE!"
            else:
                in_progress.add(ref)
                stack.append((ref, run(parsed[ref])))
                send = None

    return {name: values[name] for name in cells}
