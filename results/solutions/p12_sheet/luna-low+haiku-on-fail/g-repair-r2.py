def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 1 << 17))

    ERROR_DIV = "#DIV/0!"
    ERROR_CYCLE = "#CYCLE!"
    token_re = re.compile(
        r"\s*(?:([A-Z][1-9][0-9]?)|([A-Z]+)|([0-9]+)|(<>|<=|>=|[-+*/(),:=<>]))"
    )
    cell_re = re.compile(r"[A-Z][1-9][0-9]?")
    cache = {}
    visiting = set()

    def tokenize(text):
        return [
            m.group(1) or m.group(2) or m.group(3) or m.group(4)
            for m in token_re.finditer(text)
        ]

    def parse(text):
        tokens = tokenize(text)
        index = 0

        def peek():
            return tokens[index] if index < len(tokens) else None

        def ahead(k):
            return tokens[k] if k < len(tokens) else None

        def take():
            nonlocal index
            token = peek()
            index += 1
            return token

        def parse_expr():
            node = parse_term()
            while peek() in ("+", "-"):
                op = take()
                node = ("bin", op, node, parse_term())
            return node

        def parse_term():
            node = parse_unary()
            while peek() in ("*", "/"):
                op = take()
                node = ("bin", op, node, parse_unary())
            return node

        def parse_unary():
            if peek() == "-":
                take()
                return ("neg", parse_unary())
            return parse_atom()

        def parse_atom():
            token = take()
            if token == "(":
                node = parse_expr()
                take()  # ')'
                return node
            if token in ("SUM", "MIN", "MAX", "IF"):
                return parse_call(token)
            if token.isdigit():
                return ("num", int(token))
            return ("ref", token)

        def parse_call(func):
            take()  # '('
            if func == "IF":
                left = parse_expr()
                op = take()
                right = parse_expr()
                take()  # ','
                then_node = parse_expr()
                take()  # ','
                else_node = parse_expr()
                take()  # ')'
                return ("if", op, left, right, then_node, else_node)

            args = []
            while True:
                if (
                    peek() is not None
                    and cell_re.fullmatch(peek())
                    and ahead(index + 1) == ":"
                ):
                    start = take()
                    take()  # ':'
                    end = take()
                    args.append(("range", start, end))
                else:
                    args.append(parse_expr())
                if peek() == ",":
                    take()
                    continue
                break
            take()  # ')'
            return ("call", func, args)

        return parse_expr()

    def position(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def cell_value(name):
        if name in cache:
            return cache[name]
        if name not in cells:
            return 0
        if name in visiting:
            return ERROR_CYCLE

        visiting.add(name)
        content = cells[name]
        if content.startswith("="):
            value = evaluate(parse(content[1:]))
        else:
            value = int(content)
        visiting.discard(name)
        cache[name] = value
        return value

    def evaluate(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "ref":
            return cell_value(node[1])

        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value

        if kind == "bin":
            op = node[1]
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
            if isinstance(right, str):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return ERROR_DIV
            quotient = abs(left) // abs(right)
            return quotient if (left < 0) == (right < 0) else -quotient

        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(then_node if condition else else_node)

        # kind == "call"
        _, func, args = node
        values = []
        for arg in args:
            if arg[0] == "range":
                c1, r1 = position(arg[1])
                c2, r2 = position(arg[2])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        name = chr(ord("A") + col) + str(row)
                        if name in cells:
                            value = cell_value(name)
                            if isinstance(value, str):
                                return value
                            values.append(value)
            else:
                value = evaluate(arg)
                if isinstance(value, str):
                    return value
                values.append(value)

        if func == "SUM":
            return sum(values)
        if not values:
            return 0
        if func == "MIN":
            return min(values)
        return max(values)

    return {name: cell_value(name) for name in cells}
