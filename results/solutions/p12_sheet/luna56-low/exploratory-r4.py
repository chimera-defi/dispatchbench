def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(20000)

    def tokenize(s):
        tokens = []
        i = 0
        while i < len(s):
            if s[i].isspace():
                i += 1
            elif s.startswith("<>", i):
                tokens.append("<>")
                i += 2
            elif s.startswith("<=", i) or s.startswith(">=", i):
                tokens.append(s[i:i + 2])
                i += 2
            elif s[i] in "+-*/(),:<=>":
                tokens.append(s[i])
                i += 1
            elif s[i].isdigit():
                j = i
                while j < len(s) and s[j].isdigit():
                    j += 1
                tokens.append(s[i:j])
                i = j
            elif s[i].isalpha():
                j = i
                while j < len(s) and s[j].isalnum():
                    j += 1
                tokens.append(s[i:j])
                i = j
            else:
                i += 1
        return tokens

    class Parser:
        def __init__(self, text):
            self.t = tokenize(text)
            self.i = 0

        def peek(self):
            return self.t[self.i] if self.i < len(self.t) else None

        def take(self):
            x = self.peek()
            self.i += 1
            return x

        def expr(self):
            node = self.term()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.peek() == "-":
                self.take()
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            tok = self.take()
            if tok == "(":
                node = self.expr()
                self.take()
                return node
            if tok.isdigit():
                return ("lit", int(tok))
            if self.peek() == "(":
                self.take()
                if tok == "IF":
                    left = self.expr()
                    op = self.take()
                    right = self.expr()
                    self.take()
                    then = self.expr()
                    self.take()
                    otherwise = self.expr()
                    self.take()
                    return ("if", left, op, right, then, otherwise)

                args = []
                if self.peek() != ")":
                    while True:
                        if (
                            self.peek() is not None
                            and re.fullmatch(r"[A-Z][1-9][0-9]?", self.peek())
                            and self.i + 1 < len(self.t)
                            and self.t[self.i + 1] == ":"
                        ):
                            a = self.take()
                            self.take()
                            b = self.take()
                            args.append(("range", a, b))
                        else:
                            args.append(self.expr())
                        if self.peek() != ",":
                            break
                        self.take()
                self.take()
                return ("func", tok, args)
            return ("ref", tok)

    parsed = {}
    for name, content in cells.items():
        if re.fullmatch(r"-?\d+", content.strip()):
            parsed[name] = ("lit", int(content.strip()))
        else:
            parsed[name] = Parser(content.strip()[1:]).expr()

    state = {name: 0 for name in cells}
    values = {}

    def get_cell(name):
        if name not in cells:
            return 0
        if state[name] == 1:
            return "#CYCLE!"
        if state[name] == 2:
            return values[name]

        state[name] = 1
        values[name] = eval_node(parsed[name])
        state[name] = 2
        return values[name]

    def eval_node(node):
        kind = node[0]

        if kind == "lit":
            return node[1]

        if kind == "ref":
            return get_cell(node[1])

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

            if node[1] == "+":
                return left + right
            if node[1] == "-":
                return left - right
            if node[1] == "*":
                return left * right
            if right == 0:
                return "#DIV/0!"
            result = abs(left) // abs(right)
            return -result if (left < 0) != (right < 0) else result

        if kind == "if":
            left = eval_node(node[1])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
            if isinstance(right, str):
                return right

            op = node[2]
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

        if kind == "range":
            start, end = node[1], node[2]
            c1, r1 = ord(start[0]) - 65, int(start[1:])
            c2, r2 = ord(end[0]) - 65, int(end[1:])
            return [
                get_cell(chr(c + 65) + str(r))
                for r in range(min(r1, r2), max(r1, r2) + 1)
                for c in range(min(c1, c2), max(c1, c2) + 1)
                if chr(c + 65) + str(r) in cells
            ]

        if kind == "func":
            func, args = node[1], node[2]
            vals = []

            for arg in args:
                if arg[0] == "range":
                    part = eval_node(arg)
                    for value in part:
                        if isinstance(value, str):
                            return value
                        vals.append(value)
                else:
                    value = eval_node(arg)
                    if isinstance(value, str):
                        return value
                    vals.append(value)

            if not vals:
                return 0
            if func == "SUM":
                return sum(vals)
            if func == "MIN":
                return min(vals)
            return max(vals)

    for name in cells:
        get_cell(name)

    return {name: values[name] for name in cells}
