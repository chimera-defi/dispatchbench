def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(10000)

    token_re = re.compile(r'\s*(?:(\d+)|([A-Za-z]+\d*)|(<>|<=|>=|[+\-*/(),:()=<>]))')

    def tokenize(s):
        out = []
        pos = 0
        while pos < len(s):
            m = token_re.match(s, pos)
            if not m:
                pos += 1
                continue
            pos = m.end()
            if m.group(1) is not None:
                out.append(("num", int(m.group(1))))
            elif m.group(2) is not None:
                out.append(("id", m.group(2)))
            else:
                out.append((m.group(3), m.group(3)))
        out.append(("EOF", None))
        return out

    class Parser:
        def __init__(self, text):
            self.t = tokenize(text)
            self.i = 0

        def cur(self):
            return self.t[self.i]

        def take(self, kind=None):
            tok = self.t[self.i]
            if kind is not None and tok[0] != kind:
                raise ValueError
            self.i += 1
            return tok

        def expr(self):
            node = self.term()
            while self.cur()[0] in ("+", "-"):
                op = self.take()[0]
                node = ("bin", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.cur()[0] in ("*", "/"):
                op = self.take()[0]
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.cur()[0] == "-":
                self.take("-")
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            kind, val = self.cur()

            if kind == "num":
                self.take()
                return ("const", val)

            if kind == "id":
                name = self.take()[1]
                if self.cur()[0] != "(":
                    return ("ref", name)

                self.take("(")

                if name in ("SUM", "MIN", "MAX"):
                    args = []
                    while True:
                        if self.cur()[0] == "id" and self.t[self.i + 1][0] == ":":
                            a = self.take()[1]
                            self.take(":")
                            b = self.take("id")[1]
                            args.append(("range", a, b))
                        else:
                            args.append(("formula", self.expr()))

                        if self.cur()[0] != ",":
                            break
                        self.take(",")
                    self.take(")")
                    return ("func", name, args)

                if name == "IF":
                    left = self.expr()
                    op = self.take()[0]
                    right = self.expr()
                    self.take(",")
                    then = self.expr()
                    self.take(",")
                    otherwise = self.expr()
                    self.take(")")
                    return ("if", op, left, right, then, otherwise)

            if kind == "(":
                self.take("(")
                node = self.expr()
                self.take(")")
                return node

            raise ValueError

    asts = {}
    for name, content in cells.items():
        if content.startswith("="):
            asts[name] = Parser(content[1:]).expr()
        else:
            asts[name] = ("const", int(content))

    state = {}
    values = {}

    def cell_value(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return "#CYCLE!"
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        values[name] = evaluate(asts[name])
        state[name] = 2
        return values[name]

    def evaluate(node):
        kind = node[0]

        if kind == "const":
            return node[1]

        if kind == "ref":
            return cell_value(node[1])

        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value

        if kind == "bin":
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
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
            return -result if (left < 0) != (right < 0) else result

        if kind == "if":
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
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

            return evaluate(node[4] if cond else node[5])

        if kind == "func":
            name = node[1]
            result = [] if name == "SUM" else None
            total = 0

            for arg in node[2]:
                if arg[0] == "formula":
                    value = evaluate(arg[1])
                    if isinstance(value, str):
                        return value
                    vals = [value]
                else:
                    a, b = arg[1], arg[2]
                    c1, r1 = ord(a[0]) - 65, int(a[1:])
                    c2, r2 = ord(b[0]) - 65, int(b[1:])
                    vals = []
                    for r in range(min(r1, r2), max(r1, r2) + 1):
                        for c in range(min(c1, c2), max(c1, c2) + 1):
                            ref = chr(c + 65) + str(r)
                            if ref in cells:
                                value = cell_value(ref)
                                if isinstance(value, str):
                                    return value
                                vals.append(value)

                if name == "SUM":
                    total += sum(vals)
                elif name == "MIN":
                    result = vals[0] if result is None else min(result, *vals)
                else:
                    result = vals[0] if result is None else max(result, *vals)

            return total if name == "SUM" else (0 if result is None else result)

    for name in cells:
        cell_value(name)

    return {name: values[name] for name in cells}
