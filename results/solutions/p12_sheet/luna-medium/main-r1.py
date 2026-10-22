import re


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    tokens = re.compile(
        r"\s*(<=|>=|<>|[A-Za-z]+|[0-9]+|[()+\-*/,:=<>])"
    )

    def tokenize(text):
        result = []
        pos = 0
        while pos < len(text):
            match = tokens.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            result.append(match.group(1))
            pos = match.end()
        return result

    parsed = {}
    state = {}
    values = {}
    stack = []

    def parse_formula(name):
        ts = tokenize(cells[name][1:])
        i = 0

        def peek():
            return ts[i] if i < len(ts) else None

        def take(expected=None):
            nonlocal i
            token = peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            i += 1
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
                take("-")
                return ("neg", parse_unary())
            return parse_atom()

        def parse_atom():
            token = peek()
            if token == "(":
                take("(")
                node = parse_expr()
                take(")")
                return node
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                take()
                return ("num", int(token))
            if token[0].isalpha():
                ident = take()
                if peek() == "(":
                    take("(")
                    if ident.upper() == "IF":
                        left = parse_expr()
                        op = take()
                        if op not in ("=", "<>", "<", "<=", ">", ">="):
                            raise ValueError("Invalid formula")
                        right = parse_expr()
                        take(",")
                        yes = parse_expr()
                        take(",")
                        no = parse_expr()
                        take(")")
                        return ("if", op, left, right, yes, no)

                    args = []
                    while True:
                        start = i
                        first = peek()
                        if first is not None and re.fullmatch(r"[A-Z][1-9][0-9]?", first):
                            cell = take()
                            if peek() == ":":
                                take(":")
                                end = take()
                                if not re.fullmatch(r"[A-Z][1-9][0-9]?", end):
                                    raise ValueError("Invalid range")
                                args.append(("range", cell, end))
                            else:
                                i = start
                                args.append(("expr", parse_expr()))
                        else:
                            args.append(("expr", parse_expr()))
                        if peek() != ",":
                            break
                        take(",")
                    take(")")
                    return ("func", ident.upper(), args)

                cell = ident
                if not re.fullmatch(r"[A-Z][1-9][0-9]?", cell):
                    raise ValueError("Invalid cell")
                return ("ref", cell)
            raise ValueError("Invalid formula")

        ast = parse_expr()
        if i != len(ts):
            raise ValueError("Invalid formula")
        return ast

    for name, content in cells.items():
        if not content.startswith("="):
            values[name] = int(content)
            state[name] = 2
        else:
            parsed[name] = parse_formula(name)
            state[name] = 0

    def eval_cell(name):
        if name not in cells:
            return 0
        if state[name] == 1:
            return "#CYCLE!"
        if state[name] == 2:
            return values[name]

        state[name] = 1
        stack.append(name)
        result = eval_node(parsed[name])
        stack.pop()
        values[name] = result
        state[name] = 2
        return result

    def is_error(value):
        return isinstance(value, str)

    def eval_node(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
        if kind == "neg":
            value = eval_node(node[1])
            return value if is_error(value) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left
            right = eval_node(right_node)
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
            _, op, left_node, right_node, yes_node, no_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left
            right = eval_node(right_node)
            if is_error(right):
                return right
            test = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return eval_node(yes_node if test else no_node)
        if kind == "range":
            return node
        if kind == "func":
            _, func, args = node
            vals = []
            for arg_kind, first, *rest in args:
                if arg_kind == "expr":
                    value = eval_node(first)
                    if is_error(value):
                        return value
                    vals.append(value)
                else:
                    start, end = first, rest[0]
                    col1, row1 = ord(start[0]) - 65, int(start[1:])
                    col2, row2 = ord(end[0]) - 65, int(end[1:])
                    for row in range(min(row1, row2), max(row1, row2) + 1):
                        for col in range(min(col1, col2), max(col1, col2) + 1):
                            cell = chr(65 + col) + str(row)
                            if cell in cells:
                                value = eval_cell(cell)
                                if is_error(value):
                                    return value
                                vals.append(value)
            if func == "SUM":
                return sum(vals)
            if func == "MIN":
                return min(vals) if vals else 0
            if func == "MAX":
                return max(vals) if vals else 0
            raise ValueError("Unknown function")
        raise ValueError("Invalid expression")

    for name in cells:
        eval_cell(name)
    return {name: values[name] for name in cells}
