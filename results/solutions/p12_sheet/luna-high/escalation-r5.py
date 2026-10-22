def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(10000)

    token_re = re.compile(r"\d+|[A-Z]+[0-9]*|<>|<=|>=|[()+*/,:=-<>]")

    def tokenize(s):
        return token_re.findall(s)

    class Parser:
        def __init__(self, tokens):
            self.t = tokens
            self.i = 0

        def peek(self):
            return self.t[self.i] if self.i < len(self.t) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.i += 1
            return token

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
                self.take("-")
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            token = self.peek()
            if token == "(":
                self.take("(")
                node = self.expr()
                self.take(")")
                return node
            if token is not None and token.isdigit():
                self.take()
                return ("num", int(token))
            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.function()
            if token is not None and re.fullmatch(r"[A-Z][1-9][0-9]?", token):
                self.take()
                return ("ref", token)
            raise ValueError("Invalid formula")

        def function(self):
            name = self.take()
            self.take("(")
            if name == "IF":
                left = self.expr()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid comparison")
                right = self.expr()
                self.take(",")
                then_node = self.expr()
                self.take(",")
                else_node = self.expr()
                self.take(")")
                return ("if", op, left, right, then_node, else_node)

            args = []
            while True:
                first = self.peek()
                second = self.t[self.i + 1] if self.i + 1 < len(self.t) else None
                third = self.t[self.i + 2] if self.i + 2 < len(self.t) else None
                if (first is not None
                        and re.fullmatch(r"[A-Z][1-9][0-9]?", first)
                        and second == ":"
                        and third is not None
                        and re.fullmatch(r"[A-Z][1-9][0-9]?", third)):
                    a = self.take()
                    self.take(":")
                    b = self.take()
                    args.append(("range", a, b))
                else:
                    args.append(("formula", self.expr()))
                if self.peek() != ",":
                    break
                self.take(",")
            self.take(")")
            return ("func", name, args)

    asts = {}
    for name, content in cells.items():
        if content.startswith("="):
            parser = Parser(tokenize(content[1:]))
            asts[name] = parser.expr()
        else:
            asts[name] = ("num", int(content))

    values = {}
    active = set()
    errors = {"#DIV/0!", "#CYCLE!"}

    def coords(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def get_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return "#CYCLE!"
        active.add(name)
        value = evaluate(asts[name])
        active.remove(name)
        values[name] = value
        return value

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return get_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if value in errors else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if left in errors:
                return left
            right = evaluate(right_node)
            if right in errors:
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
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if left in errors:
                return left
            right = evaluate(right_node)
            if right in errors:
                return right
            comparison = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(then_node if comparison else else_node)

        _, name, args = node
        collected = []
        for arg in args:
            if arg[0] == "formula":
                value = evaluate(arg[1])
                if value in errors:
                    return value
                collected.append(value)
            else:
                c1, r1 = coords(arg[1])
                c2, r2 = coords(arg[2])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell = chr(ord("A") + col) + str(row)
                        if cell in cells:
                            value = get_cell(cell)
                            if value in errors:
                                return value
                            collected.append(value)

        if not collected:
            return 0
        if name == "SUM":
            return sum(collected)
        if name == "MIN":
            return min(collected)
        return max(collected)

    for cell in cells:
        get_cell(cell)
    return values
