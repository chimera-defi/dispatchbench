def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(10000, len(cells) * 4 + 100))

    tokens_re = re.compile(r"\s+|<>|<=|>=|[A-Z][0-9]+|[0-9]+|[A-Z]+|[()+\-*/:,<>=]")
    parsed = {}

    def parse(source):
        tokens = [m.group() for m in tokens_re.finditer(source) if not m.group().isspace()]
        i = 0

        def peek():
            return tokens[i] if i < len(tokens) else None

        def take(expected=None):
            nonlocal i
            token = peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            i += 1
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
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                take()
                return ("num", int(token))
            if token == "(":
                take("(")
                node = expr()
                take(")")
                return node
            if re.fullmatch(r"[A-Z][0-9]+", token):
                take()
                return ("ref", token)
            if token in ("SUM", "MIN", "MAX", "IF"):
                name = take()
                take("(")
                if name == "IF":
                    left = expr()
                    op = take()
                    if op not in ("=", "<>", "<", "<=", ">", ">="):
                        raise ValueError("Invalid comparison")
                    right = expr()
                    take(",")
                    then = expr()
                    take(",")
                    otherwise = expr()
                    take(")")
                    return ("if", op, left, right, then, otherwise)

                args = []
                while True:
                    if (
                        peek() is not None
                        and re.fullmatch(r"[A-Z][0-9]+", peek())
                        and i + 1 < len(tokens)
                        and tokens[i + 1] == ":"
                    ):
                        start = take()
                        take(":")
                        end = take()
                        args.append(("range", start, end))
                    else:
                        args.append(expr())
                    if peek() != ",":
                        break
                    take(",")
                take(")")
                return ("func", name, args)
            raise ValueError("Invalid formula")

        result = expr()
        if peek() is not None:
            raise ValueError("Invalid formula")
        return result

    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = parse(content[1:])

    in_progress = set()
    values = {}

    def is_error(value):
        return isinstance(value, str)

    def eval_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in in_progress:
            return "#CYCLE!"

        in_progress.add(name)
        content = cells[name]
        result = int(content) if not content.startswith("=") else evaluate(parsed[name])
        in_progress.remove(name)
        values[name] = result
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if is_error(value) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
            if is_error(right):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return "#DIV/0!"
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
            if is_error(right):
                return right
            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(then_node if comparisons[op] else else_node)
        if kind == "func":
            _, name, args = node
            result_values = []
            for arg in args:
                if arg[0] == "range":
                    _, start, end = arg
                    col1, row1 = ord(start[0]) - 65, int(start[1:])
                    col2, row2 = ord(end[0]) - 65, int(end[1:])
                    for row in range(min(row1, row2), max(row1, row2) + 1):
                        for col in range(min(col1, col2), max(col1, col2) + 1):
                            cell = chr(col + 65) + str(row)
                            if cell in cells:
                                value = eval_cell(cell)
                                if is_error(value):
                                    return value
                                result_values.append(value)
                else:
                    value = evaluate(arg)
                    if is_error(value):
                        return value
                    result_values.append(value)

            if name == "SUM":
                return sum(result_values)
            if not result_values:
                return 0
            if name == "MIN":
                return min(result_values)
            return max(result_values)

    return {name: eval_cell(name) for name in cells}
