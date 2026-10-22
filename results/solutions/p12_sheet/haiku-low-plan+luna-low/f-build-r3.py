def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    token_re = re.compile(
        r"\s*(<=|>=|<>|[A-Za-z]+|[0-9]+|[=+\-*/(),:<>])"
    )
    cache = {}
    in_progress = object()

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    def parse_formula(text):
        tokens = tokenize(text)
        index = 0

        def peek():
            return tokens[index] if index < len(tokens) else None

        def take(expected=None):
            nonlocal index
            token = peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            index += 1
            return token

        def expr():
            node = term()
            while peek() in ("+", "-"):
                op = take()
                node = ("bin", op, node, term())
            return node

        def term():
            node = unary()
            while peek() in ("*", "/"):
                op = take()
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() == "-":
                take("-")
                return ("neg", unary())
            return atom()

        def atom():
            token = peek()
            if token == "(":
                take("(")
                node = expr()
                take(")")
                return node
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                take()
                return ("num", int(token))
            if token.isalpha():
                name = take().upper()
                if peek() == "(":
                    take("(")
                    if name == "IF":
                        left = expr()
                        op = take()
                        if op not in ("=", "<>", "<", "<=", ">", ">="):
                            raise ValueError("Invalid formula")
                        right = expr()
                        take(",")
                        yes = expr()
                        take(",")
                        no = expr()
                        take(")")
                        return ("if", left, op, right, yes, no)

                    args = []
                    while True:
                        first = expr()
                        if peek() == ":":
                            if first[0] != "ref":
                                raise ValueError("Invalid range")
                            take(":")
                            second = expr()
                            if second[0] != "ref":
                                raise ValueError("Invalid range")
                            args.append(("range", first[1], second[1]))
                        else:
                            args.append(first)
                        if peek() != ",":
                            break
                        take(",")
                    take(")")
                    return ("call", name, args)
                if len(name) == 2 and name[0].isalpha() and name[1].isdigit():
                    return ("ref", name)
                raise ValueError("Invalid formula")
            raise ValueError("Invalid formula")

        result = expr()
        if index != len(tokens):
            raise ValueError("Invalid formula")
        return result

    def parse_cell(name):
        content = cells[name]
        if content.startswith("="):
            return parse_formula(content[1:])
        return ("num", int(content))

    def value(name):
        if name not in cells:
            return 0
        current = cache.get(name)
        if current is in_progress:
            return "#CYCLE!"
        if name in cache:
            return current

        cache[name] = in_progress
        result = evaluate(parse_cell(name))
        cache[name] = result
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return value(node[1])
        if kind == "neg":
            v = evaluate(node[1])
            return v if isinstance(v, str) else -v
        if kind == "bin":
            _, op, left, right = node
            a = evaluate(left)
            if isinstance(a, str):
                return a
            b = evaluate(right)
            if isinstance(b, str):
                return b
            if op == "+":
                return a + b
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            if b == 0:
                return "#DIV/0!"
            q = abs(a) // abs(b)
            return -q if (a < 0) != (b < 0) else q
        if kind == "if":
            _, left, op, right, yes, no = node
            a = evaluate(left)
            if isinstance(a, str):
                return a
            b = evaluate(right)
            if isinstance(b, str):
                return b
            condition = {
                "=": a == b,
                "<>": a != b,
                "<": a < b,
                "<=": a <= b,
                ">": a > b,
                ">=": a >= b,
            }[op]
            return evaluate(yes if condition else no)
        if kind == "call":
            _, function, args = node
            values = []
            for arg in args:
                if arg[0] == "range":
                    _, first, second = arg
                    c1, r1 = ord(first[0]) - 65, int(first[1:])
                    c2, r2 = ord(second[0]) - 65, int(second[1:])
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            cell = chr(col + 65) + str(row)
                            if cell in cells:
                                v = value(cell)
                                if isinstance(v, str):
                                    return v
                                values.append(v)
                else:
                    v = evaluate(arg)
                    if isinstance(v, str):
                        return v
                    values.append(v)

            if function == "SUM":
                return sum(values)
            if function == "MIN":
                return min(values) if values else 0
            if function == "MAX":
                return max(values) if values else 0
            raise ValueError("Unknown function")
        raise ValueError("Invalid expression")

    return {name: value(name) for name in cells}
