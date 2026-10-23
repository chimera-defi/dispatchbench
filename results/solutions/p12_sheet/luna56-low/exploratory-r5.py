def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(20000)

    token_re = re.compile(r'\s*(?:(\d+)|([A-Z][A-Z]?\d+)|([A-Z]+)|(<>)|(<=)|(>=)|([()+\-*/,=:<>]))')

    def tokenize(s):
        out = []
        pos = 0
        while pos < len(s):
            m = token_re.match(s, pos)
            if not m:
                pos += 1
                continue
            pos = m.end()
            if m.group(1):
                out.append(("num", int(m.group(1))))
            elif m.group(2):
                out.append(("cell", m.group(2)))
            elif m.group(3):
                out.append(("name", m.group(3)))
            elif m.group(4):
                out.append(("op", "<>"))
            elif m.group(5):
                out.append(("op", "<="))
            elif m.group(6):
                out.append(("op", ">="))
            else:
                out.append(("op", m.group(7)))
        out.append(("eof", None))
        return out

    class Parser:
        def __init__(self, text):
            self.t = tokenize(text)
            self.i = 0

        def peek(self, value=None):
            tok = self.t[self.i]
            return tok[1] == value if value is not None else tok

        def take(self, value=None):
            tok = self.t[self.i]
            if value is not None and tok[1] != value:
                raise ValueError
            self.i += 1
            return tok

        def expr(self):
            node = self.term()
            while self.peek("+") or self.peek("-"):
                op = self.take()[1]
                node = ("bin", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.peek("*") or self.peek("/"):
                op = self.take()[1]
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.peek("-"):
                self.take("-")
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            kind, value = self.take()
            if kind == "num":
                return ("num", value)
            if kind == "cell":
                return ("ref", value)
            if kind == "name":
                self.take("(")
                if value in ("SUM", "MIN", "MAX"):
                    args = []
                    while True:
                        if self.t[self.i][0] == "cell" and self.t[self.i + 1][1] == ":":
                            a = self.take()[1]
                            self.take(":")
                            b = self.take("cell")[1]
                            args.append(("range", a, b))
                        else:
                            args.append(self.expr())
                        if not self.peek(","):
                            break
                        self.take(",")
                    self.take(")")
                    return ("func", value, args)
                if value == "IF":
                    left = self.expr()
                    op = self.take()[1]
                    right = self.expr()
                    self.take(",")
                    then = self.expr()
                    self.take(",")
                    otherwise = self.expr()
                    self.take(")")
                    return ("if", op, left, right, then, otherwise)
            if value == "(":
                node = self.expr()
                self.take(")")
                return node
            raise ValueError

    parsed = {}
    for name, content in cells.items():
        text = content.strip()
        if text.startswith("="):
            parsed[name] = Parser(text[1:]).expr()
        else:
            parsed[name] = ("num", int(text))

    state = {}
    value = {}

    def col_row(name):
        i = 0
        while i < len(name) and name[i].isalpha():
            i += 1
        return ord(name[:i]) - ord("A"), int(name[i:])

    def eval_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return "#CYCLE!"
        if state.get(name) == 2:
            return value[name]
        state[name] = 1
        value[name] = eval_node(parsed[name])
        state[name] = 2
        return value[name]

    def eval_node(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "ref":
            return eval_cell(node[1])

        if kind == "neg":
            v = eval_node(node[1])
            return v if isinstance(v, str) else -v

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
            left = eval_node(node[2])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
            if isinstance(right, str):
                return right
            op = node[1]
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
            fn, args = node[1], node[2]
            vals = []
            for arg in args:
                if arg[0] == "range":
                    c1, r1 = col_row(arg[1])
                    c2, r2 = col_row(arg[2])
                    for r in range(min(r1, r2), max(r1, r2) + 1):
                        for c in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(ord("A") + c) + str(r)
                            if name in cells:
                                v = eval_cell(name)
                                if isinstance(v, str):
                                    return v
                                vals.append(v)
                else:
                    v = eval_node(arg)
                    if isinstance(v, str):
                        return v
                    vals.append(v)

            if not vals:
                return 0
            if fn == "SUM":
                return sum(vals)
            if fn == "MIN":
                return min(vals)
            return max(vals)

    for name in cells:
        eval_cell(name)
    return {name: value[name] for name in cells}
