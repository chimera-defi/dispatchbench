def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    def tokenize(text):
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
                tokens.append(("num", int(text[i:j])))
                i = j
            elif c.isupper():
                j = i
                while j < n and text[j].isupper():
                    j += 1
                if j < n and text[j].isdigit():
                    k = j
                    while k < n and text[k].isdigit():
                        k += 1
                    tokens.append(("cell", text[i:k]))
                    i = k
                else:
                    tokens.append(("id", text[i:j]))
                    i = j
            elif text.startswith("<>", i) or text.startswith("<=", i) or text.startswith(">=", i):
                tokens.append(("op", text[i:i + 2]))
                i += 2
            elif c in "+-*/=<>(),:":
                tokens.append((c, c))
                i += 1
            else:
                i += 1

        tokens.append(("eof", None))
        return tokens

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.pos = 0

        def peek(self, offset=0):
            return self.tokens[self.pos + offset]

        def take(self, kind=None):
            token = self.tokens[self.pos]
            if kind is not None and token[0] != kind:
                raise ValueError("invalid formula")
            self.pos += 1
            return token

        def parse(self):
            return self.parse_add()

        def parse_add(self):
            node = self.parse_mul()
            while self.peek()[0] in ("+", "-"):
                op = self.take()[0]
                node = ("bin", op, node, self.parse_mul())
            return node

        def parse_mul(self):
            node = self.parse_unary()
            while self.peek()[0] in ("*", "/"):
                op = self.take()[0]
                node = ("bin", op, node, self.parse_unary())
            return node

        def parse_unary(self):
            if self.peek()[0] == "-":
                self.take("-")
                return ("neg", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            kind, value = self.peek()

            if kind == "num":
                self.take()
                return ("num", value)

            if kind == "cell":
                self.take()
                return ("cell", value)

            if kind == "(":
                self.take("(")
                node = self.parse_add()
                self.take(")")
                return node

            if kind == "id":
                name = self.take("id")[1]
                self.take("(")

                if name in ("SUM", "MIN", "MAX"):
                    args = []
                    while True:
                        if self.peek()[0] == "cell" and self.peek(1)[0] == ":":
                            first = self.take("cell")[1]
                            self.take(":")
                            second = self.take("cell")[1]
                            args.append(("range", first, second))
                        else:
                            args.append(self.parse_add())

                        if self.peek()[0] != ",":
                            break
                        self.take(",")

                    self.take(")")
                    return ("func", name, args)

                if name == "IF":
                    left = self.parse_add()
                    op = self.take("op")[1] if self.peek()[0] == "op" else self.take()[1]
                    right = self.parse_add()
                    self.take(",")
                    then_node = self.parse_add()
                    self.take(",")
                    else_node = self.parse_add()
                    self.take(")")
                    return ("if", op, left, right, then_node, else_node)

            raise ValueError("invalid formula")

    state = {}
    values = {}
    parsed = {}

    def col_index(name):
        return ord(name[0]) - ord("A")

    def eval_cell(name):
        if name not in cells:
            return 0

        status = state.get(name, 0)
        if status == 1:
            return "#CYCLE!"
        if status == 2:
            return values[name]

        state[name] = 1
        content = cells[name].strip()

        if content.startswith("="):
            if name not in parsed:
                parsed[name] = Parser(content[1:]).parse()
            result = eval_node(parsed[name])
        else:
            result = int(content)

        values[name] = result
        state[name] = 2
        return result

    def eval_node(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "cell":
            return eval_cell(node[1])

        if kind == "neg":
            value = eval_node(node[1])
            if isinstance(value, str):
                return value
            return -value

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

            result = abs(left) // abs(right)
            if (left < 0) != (right < 0):
                result = -result
            return result

        if kind == "if":
            left = eval_node(node[2])
            if isinstance(left, str):
                return left

            right = eval_node(node[3])
            if isinstance(right, str):
                return right

            op = node[1]
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

            return eval_node(node[4] if condition else node[5])

        if kind == "func":
            name = node[1]
            collected = []

            for arg in node[2]:
                if arg[0] == "range":
                    first, second = arg[1], arg[2]
                    c1, c2 = col_index(first), col_index(second)
                    r1, r2 = int(first[1:]), int(second[1:])
                    lo_c, hi_c = sorted((c1, c2))
                    lo_r, hi_r = sorted((r1, r2))

                    for row in range(lo_r, hi_r + 1):
                        for col in range(lo_c, hi_c + 1):
                            cell_name = chr(ord("A") + col) + str(row)
                            if cell_name in cells:
                                value = eval_cell(cell_name)
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
            if name == "SUM":
                return sum(collected)
            if name == "MIN":
                return min(collected)
            return max(collected)

    for name in cells:
        eval_cell(name)

    return {name: values[name] for name in cells}
