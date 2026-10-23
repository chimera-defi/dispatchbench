def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(10000)

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    token_re = re.compile(r"\s*(<>|<=|>=|[()+\-*/,:=<>]|[A-Z][0-9]+|\d+)")

    def tokenize(s):
        out = []
        pos = 0
        while pos < len(s):
            m = token_re.match(s, pos)
            if not m:
                pos += 1
                continue
            out.append(m.group(1))
            pos = m.end()
        return out

    def parse_formula(s):
        tokens = tokenize(s[1:])
        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else None

        def take(expected=None):
            nonlocal pos
            t = tokens[pos]
            if expected is not None and t != expected:
                raise ValueError
            pos += 1
            return t

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
            t = peek()

            if t == "(":
                take("(")
                node = parse_add()
                take(")")
                return node

            if t is not None and t.isdigit():
                take()
                return ("num", int(t))

            if t is not None and re.fullmatch(r"[A-Z][0-9]+", t):
                take()
                return ("ref", t)

            if t in ("SUM", "MIN", "MAX"):
                fn = take()
                take("(")
                args = []
                while True:
                    if (
                        peek() is not None
                        and re.fullmatch(r"[A-Z][0-9]+", peek())
                        and pos + 1 < len(tokens)
                        and tokens[pos + 1] == ":"
                    ):
                        a = take()
                        take(":")
                        b = take()
                        args.append(("range", a, b))
                    else:
                        args.append(parse_add())

                    if peek() != ",":
                        break
                    take(",")

                take(")")
                return ("func", fn, args)

            if t == "IF":
                take("IF")
                take("(")
                left = parse_add()
                op = take()
                right = parse_add()
                take(",")
                then = parse_add()
                take(",")
                otherwise = parse_add()
                take(")")
                return ("if", op, left, right, then, otherwise)

            raise ValueError

        return parse_add()

    asts = {
        name: parse_formula(value)
        for name, value in cells.items()
        if not value.strip().lstrip("-").isdigit()
    }

    states = {}
    values = {}

    def cell_coords(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    def eval_cell(name):
        if name not in cells:
            return 0
        state = states.get(name, 0)
        if state == 1:
            return CYCLE
        if state == 2:
            return values[name]

        states[name] = 1
        text = cells[name].strip()

        if re.fullmatch(r"-?\d+", text):
            value = int(text)
        else:
            value = eval_node(asts[name])

        states[name] = 2
        values[name] = value
        return value

    def eval_node(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "ref":
            return eval_cell(node[1])

        if kind == "neg":
            value = eval_node(node[1])
            return value if isinstance(value, str) else -value

        if kind == "bin":
            op, left_node, right_node = node[1], node[2], node[3]
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
                return DIV0
            result = abs(left) // abs(right)
            return -result if (left < 0) != (right < 0) else result

        if kind == "range":
            c1, r1 = cell_coords(node[1])
            c2, r2 = cell_coords(node[2])
            return [
                eval_cell(chr(ord("A") + c) + str(r + 1))
                for r in range(min(r1, r2), max(r1, r2) + 1)
                for c in range(min(c1, c2), max(c1, c2) + 1)
                if chr(ord("A") + c) + str(r + 1) in cells
            ]

        if kind == "func":
            fn, args = node[1], node[2]
            values_list = []

            for arg in args:
                if arg[0] == "range":
                    result = eval_node(arg)
                    for value in result:
                        if isinstance(value, str):
                            return value
                        values_list.append(value)
                else:
                    value = eval_node(arg)
                    if isinstance(value, str):
                        return value
                    values_list.append(value)

            if fn == "SUM":
                return sum(values_list)
            if not values_list:
                return 0
            if fn == "MIN":
                return min(values_list)
            return max(values_list)

        if kind == "if":
            op, left_node, right_node, then_node, else_node = node[1:]
            left = eval_node(left_node)
            if isinstance(left, str):
                return left

            right = eval_node(right_node)
            if isinstance(right, str):
                return right

            if op == "=":
                condition = left == right
            elif op == "<>":
                condition = left != right
            elif op == "<":
                condition = left < right
            elif op == "<=":
                condition = left <= right
            elif op == ">":
                condition = left > right
            else:
                condition = left >= right

            return eval_node(then_node if condition else else_node)

    return {name: eval_cell(name) for name in cells}
