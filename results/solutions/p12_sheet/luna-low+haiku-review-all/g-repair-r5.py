def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import operator
    import re

    token_re = re.compile(
        r"(\d+)|([A-Z]\d+)|(SUM|MIN|MAX|IF)|(<>|<=|>=|[()+\-*/,:=<>])"
    )
    compare_ops = {
        "=": operator.eq,
        "<>": operator.ne,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
    }

    def tokenize(text):
        tokens = []
        pos = 0
        while True:
            while pos < len(text) and text[pos].isspace():
                pos += 1
            if pos == len(text):
                break
            match = token_re.match(text, pos)
            if match is None:
                raise ValueError("Invalid formula")
            number, cell, function, op = match.groups()
            if number is not None:
                tokens.append(("num", int(number)))
            elif cell is not None:
                tokens.append(("cell", cell))
            elif function is not None:
                tokens.append(("func", function))
            else:
                tokens.append((op, op))
            pos = match.end()
        tokens.append(("eof", None))
        return tokens

    def parse(text):
        tokens = tokenize(text)
        pos = 0

        def expect(kind):
            nonlocal pos
            token = tokens[pos]
            if token[0] != kind:
                raise ValueError("Invalid formula")
            pos += 1
            return token[1]

        def expression():
            nonlocal pos
            node = term()
            while tokens[pos][0] in ("+", "-"):
                op = tokens[pos][0]
                pos += 1
                node = ("bin", op, node, term())
            return node

        def term():
            nonlocal pos
            node = unary()
            while tokens[pos][0] in ("*", "/"):
                op = tokens[pos][0]
                pos += 1
                node = ("bin", op, node, unary())
            return node

        def unary():
            nonlocal pos
            if tokens[pos][0] == "-":
                pos += 1
                return ("neg", unary())
            return atom()

        def argument():
            nonlocal pos
            if tokens[pos][0] == "cell" and tokens[pos + 1][0] == ":":
                start = tokens[pos][1]
                pos += 2
                return ("range", start, expect("cell"))
            return expression()

        def atom():
            nonlocal pos
            kind, value = tokens[pos]
            if kind == "num":
                pos += 1
                return ("num", value)
            if kind == "cell":
                pos += 1
                return ("ref", value)
            if kind == "(":
                pos += 1
                node = expression()
                expect(")")
                return node
            if kind == "func":
                pos += 1
                expect("(")
                if value == "IF":
                    left = expression()
                    op = tokens[pos][0]
                    if op not in compare_ops:
                        raise ValueError("Invalid formula")
                    pos += 1
                    right = expression()
                    expect(",")
                    then_node = expression()
                    expect(",")
                    else_node = expression()
                    expect(")")
                    return ("if", op, left, right, then_node, else_node)
                args = [argument()]
                while tokens[pos][0] == ",":
                    pos += 1
                    args.append(argument())
                expect(")")
                return ("call", value, args)
            raise ValueError("Invalid formula")

        root = expression()
        expect("eof")
        return root

    def divide(a, b):
        if b == 0:
            return "#DIV/0!"
        quotient = abs(a) // abs(b)
        return quotient if (a < 0) == (b < 0) else -quotient

    def range_names(node):
        _, first, second = node
        col_lo, col_hi = sorted((ord(first[0]), ord(second[0])))
        row_lo, row_hi = sorted((int(first[1:]), int(second[1:])))
        return [
            chr(col) + str(row)
            for row in range(row_lo, row_hi + 1)
            for col in range(col_lo, col_hi + 1)
            if chr(col) + str(row) in cells
        ]

    # Each evaluator yields the name of a cell it needs and receives that
    # cell's value back. Cross-cell chains are driven by an explicit stack
    # below, so only the nesting depth of a single formula uses Python frames.
    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            if node[1] not in cells:
                return 0
            return (yield node[1])
        if kind == "neg":
            value = yield from evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            _, op, left, right = node
            a = yield from evaluate(left)
            if isinstance(a, str):
                return a
            b = yield from evaluate(right)
            if isinstance(b, str):
                return b
            if op == "+":
                return a + b
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            return divide(a, b)
        if kind == "if":
            _, op, left, right, then_node, else_node = node
            a = yield from evaluate(left)
            if isinstance(a, str):
                return a
            b = yield from evaluate(right)
            if isinstance(b, str):
                return b
            branch = then_node if compare_ops[op](a, b) else else_node
            return (yield from evaluate(branch))

        _, function, args = node
        collected = []
        for arg in args:
            if arg[0] == "range":
                for name in range_names(arg):
                    value = yield name
                    if isinstance(value, str):
                        return value
                    collected.append(value)
            else:
                value = yield from evaluate(arg)
                if isinstance(value, str):
                    return value
                collected.append(value)
        if function == "SUM":
            return sum(collected)
        if not collected:
            return 0
        return min(collected) if function == "MIN" else max(collected)

    parsed = {
        name: parse(content[1:]) if content.startswith("=") else ("num", int(content))
        for name, content in cells.items()
    }

    values = {}
    active = set()
    for root in cells:
        if root in values:
            continue
        active.add(root)
        stack = [(root, evaluate(parsed[root]))]
        send_value = None
        while stack:
            name, gen = stack[-1]
            try:
                request = gen.send(send_value)
            except StopIteration as done:
                values[name] = done.value
                active.discard(name)
                stack.pop()
                send_value = done.value
                continue
            if request in values:
                send_value = values[request]
            elif request in active:
                send_value = "#CYCLE!"
            else:
                active.add(request)
                stack.append((request, evaluate(parsed[request])))
                send_value = None

    return {name: values[name] for name in cells}
