def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(100000)

    class Parser:
        def __init__(self, text):
            self.tokens = self.tokenize(text)
            self.pos = 0

        def tokenize(self, text):
            tokens = []
            i = 0
            n = len(text)

            while i < n:
                c = text[i]

                if c.isspace():
                    i += 1
                elif c.isdigit():
                    j = i
                    while j < n and text[j].isdigit():
                        j += 1
                    tokens.append(("NUM", text[i:j]))
                    i = j
                elif "A" <= c <= "Z":
                    j = i
                    while j < n and "A" <= text[j] <= "Z":
                        j += 1
                    while j < n and text[j].isdigit():
                        j += 1
                    tokens.append(("ID", text[i:j]))
                    i = j
                elif text.startswith("<>", i):
                    tokens.append(("OP", "<>"))
                    i += 2
                elif text.startswith("<=", i) or text.startswith(">=", i):
                    tokens.append(("OP", text[i:i + 2]))
                    i += 2
                elif c in "+-*/(),:":
                    tokens.append(("OP", c))
                    i += 1
                elif c in "=<>":
                    tokens.append(("OP", c))
                    i += 1
                else:
                    i += 1

            tokens.append(("EOF", ""))
            return tokens

        def peek(self, value=None):
            token = self.tokens[self.pos]
            return token[1] == value if value is not None else token

        def take(self, value=None):
            token = self.tokens[self.pos]
            if value is not None and token[1] != value:
                raise ValueError("invalid formula")
            self.pos += 1
            return token

        def parse(self):
            return self.parse_expr()

        def parse_expr(self):
            return self.parse_add()

        def parse_add(self):
            node = self.parse_mul()
            while self.peek("+") or self.peek("-"):
                op = self.take()[1]
                node = ("bin", op, node, self.parse_mul())
            return node

        def parse_mul(self):
            node = self.parse_unary()
            while self.peek("*") or self.peek("/"):
                op = self.take()[1]
                node = ("bin", op, node, self.parse_unary())
            return node

        def parse_unary(self):
            if self.peek("-"):
                self.take("-")
                return ("un", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            kind, value = self.peek()

            if kind == "NUM":
                self.take()
                return ("num", int(value))

            if kind == "ID":
                self.take()
                if self.peek("("):
                    return self.parse_call(value)
                return ("ref", value)

            if self.peek("("):
                self.take("(")
                node = self.parse_expr()
                self.take(")")
                return node

            raise ValueError("invalid formula")

        def parse_call(self, name):
            self.take("(")

            if name == "IF":
                left = self.parse_expr()
                op = self.take()[1]
                right = self.parse_expr()
                self.take(",")
                then_node = self.parse_expr()
                self.take(",")
                else_node = self.parse_expr()
                self.take(")")
                return ("if", op, left, right, then_node, else_node)

            args = []
            while True:
                if (
                    self.peek()[0] == "ID"
                    and self.tokens[self.pos + 1][1] == ":"
                    and self.tokens[self.pos + 2][0] == "ID"
                ):
                    first = self.take()[1]
                    self.take(":")
                    second = self.take()[1]
                    args.append(("range", first, second))
                else:
                    args.append(self.parse_expr())

                if self.peek(","):
                    self.take(",")
                else:
                    break

            self.take(")")
            return ("call", name, args)

    error_types = (str,)
    state = {}
    values = {}
    trees = {}

    def is_error(value):
        return isinstance(value, error_types) and value in ("#DIV/0!", "#CYCLE!")

    def eval_cell(name):
        if name not in cells:
            return 0

        if state.get(name) == 1:
            return "#CYCLE!"
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        raw = cells[name].strip()

        if raw.startswith("="):
            trees[name] = Parser(raw[1:]).parse()
            result = eval_node(trees[name])
        else:
            result = int(raw)

        values[name] = result
        state[name] = 2
        return result

    def eval_node(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "ref":
            return eval_cell(node[1])

        if kind == "un":
            value = eval_node(node[1])
            return value if is_error(value) else -value

        if kind == "bin":
            op, left_node, right_node = node[1], node[2], node[3]
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

            result = abs(left) // abs(right)
            if (left < 0) != (right < 0):
                result = -result
            return result

        if kind == "if":
            op, left_node, right_node, then_node, else_node = node[1:]
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

        if kind == "call":
            name, args = node[1], node[2]
            total = 0
            best = None

            for arg in args:
                if arg[0] == "range":
                    c1, r1 = arg[1][0], int(arg[1][1:])
                    c2, r2 = arg[2][0], int(arg[2][1:])
                    c_start, c_end = sorted((ord(c1), ord(c2)))
                    r_start, r_end = sorted((r1, r2))

                    items = (
                        chr(col) + str(row)
                        for row in range(r_start, r_end + 1)
                        for col in range(c_start, c_end + 1)
                        if chr(col) + str(row) in cells
                    )
                else:
                    items = (None,)

                for cell_name in items:
                    value = (
                        eval_cell(cell_name)
                        if cell_name is not None
                        else eval_node(arg)
                    )

                    if is_error(value):
                        return value

                    if name == "SUM":
                        total += value
                    elif best is None:
                        best = value
                    elif name == "MIN":
                        best = min(best, value)
                    else:
                        best = max(best, value)

            if name == "SUM":
                return total
            return 0 if best is None else best

        raise ValueError("invalid node")

    for name in cells:
        eval_cell(name)

    return {name: values[name] for name in cells}
