def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(10000)

    token_re = re.compile(r"\s*(?:(\d+)|([A-Za-z][A-Za-z0-9]*)|(<>|<=|>=|[+\-*/(),:()<>=]))")

    def tokenize(s):
        out = []
        pos = 0
        while pos < len(s):
            m = token_re.match(s, pos)
            if not m:
                break
            if m.group(1) is not None:
                out.append(("num", int(m.group(1))))
            elif m.group(2) is not None:
                out.append(("id", m.group(2)))
            else:
                out.append((m.group(3), m.group(3)))
            pos = m.end()
        out.append(("EOF", None))
        return out

    def is_cell_name(name):
        return (
            len(name) >= 2
            and name[0].isalpha()
            and name[0].isupper()
            and name[1:].isdigit()
            and 1 <= int(name[1:]) <= 99
        )

    def parse_formula(text):
        toks = tokenize(text[1:])
        i = 0

        def peek(value=None):
            return toks[i][0] == value if value is not None else toks[i]

        def take(value=None):
            nonlocal i
            t = toks[i]
            if value is not None and t[0] != value:
                raise ValueError("invalid formula")
            i += 1
            return t

        def parse_expr():
            nonlocal i
            node = parse_term()
            while peek("+") or peek("-"):
                op = take()[0]
                node = ("bin", op, node, parse_term())
            return node

        def parse_term():
            nonlocal i
            node = parse_unary()
            while peek("*") or peek("/"):
                op = take()[0]
                node = ("bin", op, node, parse_unary())
            return node

        def parse_unary():
            if peek("-"):
                take("-")
                return ("neg", parse_unary())
            return parse_atom()

        def parse_atom():
            nonlocal i
            if peek("num"):
                return ("const", take("num")[1])

            if peek("("):
                take("(")
                node = parse_expr()
                take(")")
                return node

            name = take("id")[1]

            if peek("("):
                take("(")
                if name == "IF":
                    left = parse_expr()
                    op = take()[0]
                    right = parse_expr()
                    take(",")
                    then_node = parse_expr()
                    take(",")
                    else_node = parse_expr()
                    take(")")
                    return ("if", left, op, right, then_node, else_node)

                args = []
                if not peek(")"):
                    while True:
                        if (
                            peek("id")
                            and is_cell_name(toks[i][1])
                            and toks[i + 1][0] == ":"
                        ):
                            first = take("id")[1]
                            take(":")
                            second = take("id")[1]
                            args.append(("range", first, second))
                        else:
                            args.append(("formula_arg", parse_expr()))
                        if not peek(","):
                            break
                        take(",")
                take(")")
                return ("func", name, args)

            return ("cell", name)

        return parse_expr()

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = parse_formula(content)
        else:
            parsed[name] = ("const", int(content))

    state = {}
    values = {}

    def col_row(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    def eval_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return "#CYCLE!"
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        value = eval_node(parsed[name])
        values[name] = value
        state[name] = 2
        return value

    def eval_node(node):
        kind = node[0]

        if kind == "const":
            return node[1]

        if kind == "cell":
            return eval_cell(node[1])

        if kind == "neg":
            value = eval_node(node[1])
            return value if isinstance(value, str) else -value

        if kind == "bin":
            left = eval_node(node[2])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
            if isinstance(right, str):
                return right

            op = node[1]
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return "#DIV/0!"
            q = abs(left) // abs(right)
            return -q if (left < 0) != (right < 0) else q

        if kind == "if":
            left = eval_node(node[1])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
            if isinstance(right, str):
                return right

            op = node[2]
            if op == "=":
                cond = left == right
            elif op == "<>":
                cond = left != right
            elif op == "<":
                cond = left < right
            elif op == "<=":
                cond = left <= right
            elif op == ">":
                cond = left > right
            else:
                cond = left >= right

            return eval_node(node[4] if cond else node[5])

        if kind == "func":
            name, args = node[1], node[2]
            values_seen = []

            for arg_kind, arg_a, *rest in args:
                if arg_kind == "formula_arg":
                    value = eval_node(arg_a)
                    if isinstance(value, str):
                        return value
                    values_seen.append(value)
                else:
                    c1, c2 = col_row(arg_a), col_row(rest[0])
                    min_col, max_col = sorted((c1[0], c2[0]))
                    min_row, max_row = sorted((c1[1], c2[1]))

                    for row in range(min_row, max_row + 1):
                        for col in range(min_col, max_col + 1):
                            cell_name = chr(ord("A") + col) + str(row + 1)
                            if cell_name in cells:
                                value = eval_cell(cell_name)
                                if isinstance(value, str):
                                    return value
                                values_seen.append(value)

            if not values_seen:
                return 0
            if name == "SUM":
                return sum(values_seen)
            if name == "MIN":
                return min(values_seen)
            return max(values_seen)

    for name in cells:
        eval_cell(name)

    return {name: values[name] for name in cells}
