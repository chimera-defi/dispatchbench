def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(100000)

    token_re = re.compile(r"\s*(<=|>=|<>|[()+\-*/,:<>=]|\d+|[A-Z][A-Z0-9]*)")

    class Parser:
        def __init__(self, text):
            self.tokens = []
            pos = 0
            while pos < len(text):
                match = token_re.match(text, pos)
                if not match:
                    raise ValueError("invalid formula")
                self.tokens.append(match.group(1))
                pos = match.end()
            self.tokens.append(None)
            self.i = 0

        def peek(self):
            return self.tokens[self.i]

        def take(self, token=None):
            value = self.tokens[self.i]
            if token is not None and value != token:
                raise ValueError("unexpected token")
            self.i += 1
            return value

        def parse(self):
            return self.parse_add()

        def parse_add(self):
            node = self.parse_mul()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.parse_mul())
            return node

        def parse_mul(self):
            node = self.parse_unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("bin", op, node, self.parse_unary())
            return node

        def parse_unary(self):
            if self.peek() == "-":
                self.take("-")
                return ("neg", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            token = self.peek()

            if token is None:
                raise ValueError("unexpected end")

            if token.isdigit():
                self.take()
                return ("num", int(token))

            if token == "(":
                self.take("(")
                node = self.parse_add()
                self.take(")")
                return node

            name = self.take()

            if self.peek() == "(":
                self.take("(")

                if name == "IF":
                    left = self.parse_add()
                    op = self.take()
                    right = self.parse_add()
                    self.take(",")
                    then_node = self.parse_add()
                    self.take(",")
                    else_node = self.parse_add()
                    self.take(")")
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    if (
                        self.peek() is not None
                        and re.fullmatch(r"[A-Z][0-9]+", self.peek() or "")
                        and self.i + 1 < len(self.tokens)
                        and self.tokens[self.i + 1] == ":"
                    ):
                        start = self.take()
                        self.take(":")
                        end = self.take()
                        args.append(("range", start, end))
                    else:
                        args.append(self.parse_add())

                    if self.peek() == ",":
                        self.take(",")
                    else:
                        break

                self.take(")")
                return ("func", name, args)

            return ("ref", name)

    state = {}
    values = {}
    trees = {}

    for name, content in cells.items():
        stripped = content.strip()
        if stripped.startswith("="):
            trees[name] = Parser(stripped[1:]).parse()
        else:
            values[name] = int(stripped)
            state[name] = 2

    def is_error(value):
        return isinstance(value, str)

    def coord(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    def eval_cell(name):
        if name not in cells:
            return 0

        status = state.get(name, 0)
        if status == 1:
            return "#CYCLE!"
        if status == 2:
            return values[name]

        state[name] = 1
        result = eval_node(trees[name])
        values[name] = result
        state[name] = 2
        return result

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
            return quotient if (left >= 0) == (right >= 0) else -quotient

        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left

            right = eval_node(right_node)
            if is_error(right):
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

        _, function, args = node
        values_seen = []

        for arg in args:
            if arg[0] == "range":
                _, start, end = arg
                c1, r1 = coord(start)
                c2, r2 = coord(end)

                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell_name = chr(ord("A") + col) + str(row + 1)
                        if cell_name in cells:
                            value = eval_cell(cell_name)
                            if is_error(value):
                                return value
                            values_seen.append(value)
            else:
                value = eval_node(arg)
                if is_error(value):
                    return value
                values_seen.append(value)

        if function == "SUM":
            return sum(values_seen)
        if function == "MIN":
            return min(values_seen) if values_seen else 0
        return max(values_seen) if values_seen else 0

    for name in cells:
        eval_cell(name)

    return {name: values[name] for name in cells}
