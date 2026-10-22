def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    ERROR_DIV = "#DIV/0!"
    ERROR_CYCLE = "#CYCLE!"

    # Tokenize formulas, ignoring whitespace.
    token_re = re.compile(
        r"\s*(<=|>=|<>|[A-Z](?:[1-9][0-9]?)?|-?[0-9]+|[()+*/,:=<>-])"
    )

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

    parsed = {}
    states = {}  # 1 = evaluating, 2 = evaluated
    values = {}

    def parse_formula(text):
        tokens = tokenize(text)
        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else None

        def take(expected=None):
            nonlocal pos
            token = peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            pos += 1
            return token

        def parse_add():
            node = parse_mul()
            while peek() in ("+", "-"):
                op = take()
                node = ("bin", op, node, parse_mul())
            return node

        def parse_mul():
            node = parse_unary()
            while peek() in ("*", "/"):
                op = take()
                node = ("bin", op, node, parse_unary())
            return node

        def parse_unary():
            if peek() == "-":
                take("-")
                return ("neg", parse_unary())
            return parse_atom()

        def parse_atom():
            token = peek()
            if token == "(":
                take("(")
                node = parse_add()
                take(")")
                return node

            if token is None:
                raise ValueError("Invalid formula")

            if token.isdigit():
                take()
                return ("lit", int(token))

            if token.isalpha() and len(token) == 1:
                name = take() + take()
                return ("ref", name)

            if token in ("SUM", "MIN", "MAX", "IF"):
                func = take()
                take("(")
                if func == "IF":
                    left = parse_add()
                    op = take()
                    if op not in ("=", "<>", "<", "<=", ">", ">="):
                        raise ValueError("Invalid formula")
                    right = parse_add()
                    take(",")
                    then_node = parse_add()
                    take(",")
                    else_node = parse_add()
                    take(")")
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    # A range is recognized by a cell name immediately followed by ':'.
                    if (
                        peek() is not None
                        and len(peek()) >= 2
                        and peek()[0].isalpha()
                        and pos + 1 < len(tokens)
                        and tokens[pos + 1] == ":"
                    ):
                        first = take() + take()
                        take(":")
                        second = take() + take()
                        args.append(("range", first, second))
                    else:
                        args.append(parse_add())
                    if peek() != ",":
                        break
                    take(",")
                take(")")
                return ("call", func, args)

            raise ValueError("Invalid formula")

        root = parse_add()
        if pos != len(tokens):
            raise ValueError("Invalid formula")
        return root

    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = parse_formula(content[1:])
        else:
            values[name] = int(content)
            states[name] = 2

    def cell_value(name):
        if name not in cells:
            return 0
        state = states.get(name, 0)
        if state == 1:
            return ERROR_CYCLE
        if state == 2:
            return values[name]

        states[name] = 1
        result = eval_node(parsed[name])
        values[name] = result
        states[name] = 2
        return result

    def eval_node(node):
        kind = node[0]

        if kind == "lit":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            value = eval_node(node[1])
            return value if isinstance(value, str) else -value

        if kind == "bin":
            _, op, left_node, right_node = node
            left = eval_node(left_node)
            if isinstance(left, str):
                return left
            right = eval_node(right_node)
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
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = eval_node(left_node)
            if isinstance(left, str):
                return left
            right = eval_node(right_node)
            if isinstance(right, str):
                return right
            conditions = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return eval_node(then_node if conditions[op] else else_node)

        _, func, args = node
        collected = []
        for arg in args:
            if arg[0] == "range":
                _, first, second = arg
                col1, row1 = ord(first[0]) - ord("A"), int(first[1:])
                col2, row2 = ord(second[0]) - ord("A"), int(second[1:])
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        name = chr(ord("A") + col) + str(row)
                        if name not in cells:
                            continue
                        value = cell_value(name)
                        if isinstance(value, str):
                            return value
                        collected.append(value)
            else:
                value = eval_node(arg)
                if isinstance(value, str):
                    return value
                collected.append(value)

        if not collected:
            return 0
        if func == "SUM":
            return sum(collected)
        if func == "MIN":
            return min(collected)
        return max(collected)

    return {name: cell_value(name) for name in cells}
