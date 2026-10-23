def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    total_size = sum(len(value) for value in cells.values())
    needed_limit = total_size * 2 + len(cells) * 4 + 1000
    if sys.getrecursionlimit() < needed_limit:
        sys.setrecursionlimit(needed_limit)

    class Parser:
        def __init__(self, source):
            self.tokens = []
            self.pos = 0
            i = 0

            while i < len(source):
                ch = source[i]

                if ch.isspace():
                    i += 1
                elif ch.isdigit():
                    j = i + 1
                    while j < len(source) and source[j].isdigit():
                        j += 1
                    self.tokens.append(("NUM", int(source[i:j])))
                    i = j
                elif "A" <= ch <= "Z":
                    j = i + 1
                    while j < len(source) and (
                        "A" <= source[j] <= "Z" or source[j].isdigit()
                    ):
                        j += 1
                    word = source[i:j]
                    if len(word) >= 2 and len(word.split(word[0], 1)[-1]) > 0 \
                            and len(word[0]) == 1 and word[1:].isdigit():
                        self.tokens.append(("CELL", word))
                    else:
                        self.tokens.append(("ID", word))
                    i = j
                elif source.startswith("<=", i) or source.startswith(">=", i) \
                        or source.startswith("<>", i):
                    self.tokens.append((source[i:i + 2], source[i:i + 2]))
                    i += 2
                else:
                    self.tokens.append((ch, ch))
                    i += 1

            self.tokens.append(("EOF", None))

        def peek(self, offset=0):
            return self.tokens[self.pos + offset]

        def take(self, kind=None):
            token = self.tokens[self.pos]
            if kind is not None:
                assert token[0] == kind
            self.pos += 1
            return token

        def parse(self):
            result = self.parse_add()
            self.take("EOF")
            return result

        def parse_add(self):
            node = self.parse_mul()
            while self.peek()[0] in ("+", "-"):
                op = self.take()[0]
                node = ("binary", op, node, self.parse_mul())
            return node

        def parse_mul(self):
            node = self.parse_unary()
            while self.peek()[0] in ("*", "/"):
                op = self.take()[0]
                node = ("binary", op, node, self.parse_unary())
            return node

        def parse_unary(self):
            if self.peek()[0] == "-":
                self.take("-")
                return ("neg", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            kind, value = self.peek()

            if kind == "NUM":
                self.take()
                return ("number", value)

            if kind == "CELL":
                self.take()
                return ("cell", value)

            if kind == "(":
                self.take("(")
                node = self.parse_add()
                self.take(")")
                return node

            name = self.take("ID")[1]
            self.take("(")

            if name == "IF":
                left = self.parse_add()
                op = self.take()[0]
                assert op in ("=", "<>", "<", "<=", ">", ">=")
                right = self.parse_add()
                self.take(",")
                then_branch = self.parse_add()
                self.take(",")
                else_branch = self.parse_add()
                self.take(")")
                return ("if", op, left, right, then_branch, else_branch)

            args = []
            while True:
                if self.peek()[0] == "CELL" and self.peek(1)[0] == ":":
                    start = self.take("CELL")[1]
                    self.take(":")
                    end = self.take("CELL")[1]
                    args.append(("range", start, end))
                else:
                    args.append(("formula", self.parse_add()))

                if self.peek()[0] != ",":
                    break
                self.take(",")

            self.take(")")
            return ("function", name, args)

    expressions = {}
    for name, content in cells.items():
        if content.startswith("="):
            expressions[name] = Parser(content[1:]).parse()
        else:
            expressions[name] = ("number", int(content))

    state = {}
    values = {}
    DIV_ZERO = "#DIV/0!"
    CYCLE = "#CYCLE!"

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return CYCLE
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        value = evaluate(expressions[name])
        values[name] = value
        state[name] = 2
        return value

    def evaluate(node):
        kind = node[0]

        if kind == "number":
            return node[1]

        if kind == "cell":
            return evaluate_cell(node[1])

        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value

        if kind == "binary":
            op, left_node, right_node = node[1:]
            left = evaluate(left_node)
            if isinstance(left, str):
                return left

            right = evaluate(right_node)
            if isinstance(right, str):
                return right

            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return DIV_ZERO

            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            op, left_node, right_node, then_node, else_node = node[1:]
            left = evaluate(left_node)
            if isinstance(left, str):
                return left

            right = evaluate(right_node)
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

            return evaluate(then_node if condition else else_node)

        name, args = node[1], node[2]
        result = 0
        best = None

        def accept(value):
            nonlocal result, best
            if name == "SUM":
                result += value
            elif best is None:
                best = value
            elif name == "MIN":
                best = min(best, value)
            else:
                best = max(best, value)

        for arg in args:
            if arg[0] == "formula":
                value = evaluate(arg[1])
                if isinstance(value, str):
                    return value
                accept(value)
                continue

            start, end = arg[1], arg[2]
            col_lo = min(ord(start[0]), ord(end[0]))
            col_hi = max(ord(start[0]), ord(end[0]))
            row_lo = min(int(start[1:]), int(end[1:]))
            row_hi = max(int(start[1:]), int(end[1:]))

            for row in range(row_lo, row_hi + 1):
                for col in range(col_lo, col_hi + 1):
                    cell_name = chr(col) + str(row)
                    if cell_name not in cells:
                        continue
                    value = evaluate_cell(cell_name)
                    if isinstance(value, str):
                        return value
                    accept(value)

        return result if name == "SUM" or best is None else best

    return {name: evaluate_cell(name) for name in cells}
