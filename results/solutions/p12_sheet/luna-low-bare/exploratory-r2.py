def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    token_re = re.compile(
        r"\s*(<=|>=|<>|[A-Za-z]+[1-9][0-9]?|[0-9]+|[()+*/,:-]|=|<|>)"
    )

    class Parser:
        def __init__(self, text):
            self.tokens = []
            pos = 0
            while pos < len(text):
                match = token_re.match(text, pos)
                if not match:
                    raise ValueError("Invalid formula")
                self.tokens.append(match.group(1))
                pos = match.end()
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.i += 1
            return token

        def formula(self):
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
            token = self.peek()
            if token == "(":
                self.take("(")
                node = self.formula()
                self.take(")")
                return node
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                self.take()
                return ("num", int(token))
            if re.fullmatch(r"[A-Z][1-9][0-9]?", token):
                self.take()
                return ("ref", token)
            if token in ("SUM", "MIN", "MAX", "IF"):
                name = self.take()
                self.take("(")
                if name == "IF":
                    left = self.formula()
                    op = self.take()
                    if op not in ("=", "<>", "<", "<=", ">", ">="):
                        raise ValueError("Invalid formula")
                    right = self.formula()
                    self.take(",")
                    yes = self.formula()
                    self.take(",")
                    no = self.formula()
                    self.take(")")
                    return ("if", op, left, right, yes, no)

                args = []
                while True:
                    if (self.i + 2 < len(self.tokens)
                            and re.fullmatch(r"[A-Z][1-9][0-9]?", self.tokens[self.i])
                            and self.tokens[self.i + 1] == ":"
                            and re.fullmatch(r"[A-Z][1-9][0-9]?", self.tokens[self.i + 2])):
                        first = self.take()
                        self.take(":")
                        second = self.take()
                        args.append(("range", first, second))
                    else:
                        args.append(("formula", self.formula()))
                    if self.peek() != ",":
                        break
                    self.take(",")
                self.take(")")
                return ("func", name, args)
            raise ValueError("Invalid formula")

    parsed = {}
    for name, content in cells.items():
        parsed[name] = None if re.fullmatch(r"\s*-?[0-9]+\s*", content) else Parser(content.lstrip()[1:]).formula()

    values = {}
    active = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return CYCLE
        active.add(name)
        tree = parsed[name]
        if tree is None:
            result = int(cells[name].strip())
        else:
            result = evaluate(tree)
        active.remove(name)
        values[name] = result
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
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
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
            if isinstance(right, str):
                return right
            op = node[1]
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(node[4] if condition else node[5])

        _, name, args = node
        collected = []
        for arg in args:
            if arg[0] == "formula":
                value = evaluate(arg[1])
                if isinstance(value, str):
                    return value
                collected.append(value)
            else:
                _, first, second = arg
                c1, r1 = ord(first[0]) - 65, int(first[1:])
                c2, r2 = ord(second[0]) - 65, int(second[1:])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell = chr(65 + col) + str(row)
                        if cell in cells:
                            value = cell_value(cell)
                            if isinstance(value, str):
                                return value
                            collected.append(value)
        if name == "SUM":
            return sum(collected)
        if not collected:
            return 0
        return min(collected) if name == "MIN" else max(collected)

    return {name: cell_value(name) for name in cells}
