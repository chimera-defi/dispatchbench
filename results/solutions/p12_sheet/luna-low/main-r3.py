def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    TOKEN_RE = re.compile(
        r"\s*(<=|>=|<>|[()+\-*/,:=<>]|[A-Za-z]+|\d+)"
    )

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = TOKEN_RE.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    def cell_coords(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.i += 1
            return token

        def parse(self):
            node = self.expression()
            if self.peek() is not None:
                raise ValueError("Invalid formula")
            return node

        def expression(self):
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
            token = self.take()
            if token == "(":
                node = self.expression()
                self.take(")")
                return node
            if token.isdigit():
                return ("num", int(token))
            if self.peek() == "(":
                return self.function(token)
            return ("ref", token)

        def function(self, name):
            self.take("(")
            if name == "IF":
                left = self.expression()
                op = self.take()
                right = self.expression()
                self.take(",")
                yes = self.expression()
                self.take(",")
                no = self.expression()
                self.take(")")
                return ("if", left, op, right, yes, no)

            args = []
            while True:
                first = self.peek()
                if first is None:
                    raise ValueError("Invalid formula")

                # A range is a cell name, colon, cell name.
                if (len(first) >= 2 and first[0].isalpha()
                        and first[1:].isdigit()
                        and self.i + 1 < len(self.tokens)
                        and self.tokens[self.i + 1] == ":"):
                    start = self.take()
                    self.take(":")
                    end = self.take()
                    args.append(("range", start, end))
                else:
                    args.append(self.expression())

                if self.peek() != ",":
                    break
                self.take(",")
            self.take(")")
            return ("func", name, args)

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = Parser(tokenize(content[1:])).parse()
        else:
            parsed[name] = int(content)

    values = {}
    visiting = set()

    def evaluate_cell(name):
        if name not in parsed:
            return 0
        if name in values:
            return values[name]
        if name in visiting:
            return "#CYCLE!"

        visiting.add(name)
        node = parsed[name]
        value = node if isinstance(node, int) else evaluate(node)
        visiting.remove(name)
        values[name] = value
        return value

    def is_error(value):
        return isinstance(value, str)

    def evaluate(node):
        kind = node[0]

        if kind == "num":
            return node[1]
        if kind == "ref":
            return evaluate_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if is_error(value) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
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
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, left_node, op, right_node, yes_node, no_node = node
            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
            if is_error(right):
                return right
            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(yes_node if comparisons[op] else no_node)
        if kind == "func":
            _, name, args = node
            items = []
            for arg in args:
                if arg[0] == "range":
                    _, start, end = arg
                    c1, r1 = cell_coords(start)
                    c2, r2 = cell_coords(end)
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            cell_name = chr(ord("A") + col) + str(row + 1)
                            if cell_name not in parsed:
                                continue
                            value = evaluate_cell(cell_name)
                            if is_error(value):
                                return value
                            items.append(value)
                else:
                    value = evaluate(arg)
                    if is_error(value):
                        return value
                    items.append(value)
            if name == "SUM":
                return sum(items)
            if name == "MIN":
                return min(items) if items else 0
            return max(items) if items else 0

        raise ValueError("Invalid formula")

    return {name: evaluate_cell(name) for name in cells}
