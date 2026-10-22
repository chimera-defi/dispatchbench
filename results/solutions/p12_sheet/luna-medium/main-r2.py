def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    values = {}
    active = set()

    def tokenize(text):
        tokens = []
        i = 0
        n = len(text)
        while i < n:
            c = text[i]
            if c.isspace():
                i += 1
            elif c.isdigit():
                j = i + 1
                while j < n and text[j].isdigit():
                    j += 1
                tokens.append(("num", int(text[i:j])))
                i = j
            elif c.isalpha():
                j = i + 1
                while j < n and text[j].isdigit():
                    j += 1
                name = text[i:j]
                if len(name) > 1:
                    tokens.append(("cell", name))
                else:
                    tokens.append(("ident", name))
                i = j
            elif text.startswith("<>", i) or text.startswith("<=", i) or text.startswith(">=", i):
                tokens.append(("op", text[i:i + 2]))
                i += 2
            else:
                tokens.append((c, c))
                i += 1
        tokens.append(("eof", None))
        return tokens

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos][0]

        def take(self):
            tok = self.tokens[self.pos]
            self.pos += 1
            return tok

        def accept(self, kind):
            if self.peek() == kind:
                return self.take()
            return None

        def expression(self):
            node = self.term()
            while self.peek() in ("+", "-"):
                op = self.take()[0]
                node = ("bin", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()[0]
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.accept("-"):
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            kind, value = self.take()
            if kind == "num":
                return ("num", value)
            if kind == "cell":
                return ("cell", value)
            if kind == "(":
                node = self.expression()
                self.take()  # )
                return node
            if kind == "ident":
                func = value.upper()
                self.take()  # (
                if func == "IF":
                    left = self.expression()
                    op = self.take()[1]
                    right = self.expression()
                    self.take()  # ,
                    yes = self.expression()
                    self.take()  # ,
                    no = self.expression()
                    self.take()  # )
                    return ("if", left, op, right, yes, no)

                args = []
                while True:
                    first = self.expression()
                    if self.accept(":"):
                        second = self.expression()
                        args.append(("range", first, second))
                    else:
                        args.append(("formula", first))
                    if not self.accept(","):
                        break
                self.take()  # )
                return ("func", func, args)
            raise ValueError("invalid formula")

    def parse_cell(name):
        col = ord(name[0]) - ord("A")
        row = int(name[1:]) - 1
        return col, row

    def eval_node(node):
        kind = node[0]
        if kind == "num":
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
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            left = eval_node(node[1])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
            if isinstance(right, str):
                return right
            op = node[2]
            matched = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return eval_node(node[4] if matched else node[5])
        if kind == "func":
            func, args = node[1], node[2]
            items = []
            for arg in args:
                if arg[0] == "formula":
                    value = eval_node(arg[1])
                    if isinstance(value, str):
                        return value
                    items.append(value)
                else:
                    start = arg[1]
                    end = arg[2]
                    if start[0] != "cell" or end[0] != "cell":
                        continue
                    c1, r1 = parse_cell(start[1])
                    c2, r2 = parse_cell(end[1])
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(ord("A") + col) + str(row + 1)
                            if name in cells:
                                value = eval_cell(name)
                                if isinstance(value, str):
                                    return value
                                items.append(value)
            if not items:
                return 0
            if func == "SUM":
                return sum(items)
            if func == "MIN":
                return min(items)
            return max(items)
        raise ValueError("invalid node")

    def eval_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return CYCLE
        active.add(name)
        content = cells[name]
        if content.startswith("="):
            result = eval_node(Parser(tokenize(content[1:])).expression())
        else:
            result = int(content.strip())
        active.remove(name)
        values[name] = result
        return result

    return {name: eval_cell(name) for name in cells}
