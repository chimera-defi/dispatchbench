def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    class Parser:
        def __init__(self, text):
            self.tokens = re.findall(
                r'\s*(<=|>=|<>|[A-Z](?:[1-9]\d?)|[0-9]+|[A-Za-z_]+|.)', text
            )
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("invalid formula")
            self.i += 1
            return token

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
            if re.fullmatch(r"[A-Z][1-9]\d?", token):
                return ("ref", token)
            if token in ("SUM", "MIN", "MAX"):
                self.take("(")
                args = [self.argument()]
                while self.peek() == ",":
                    self.take(",")
                    args.append(self.argument())
                self.take(")")
                return ("func", token, args)
            if token == "IF":
                self.take("(")
                left = self.expression()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("invalid comparison")
                right = self.expression()
                self.take(",")
                yes = self.expression()
                self.take(",")
                no = self.expression()
                self.take(")")
                return ("if", left, op, right, yes, no)
            raise ValueError("invalid atom")

        def argument(self):
            # A range starts with a cell name immediately followed by ':'.
            if (self.i + 1 < len(self.tokens)
                    and re.fullmatch(r"[A-Z][1-9]\d?", self.tokens[self.i])
                    and self.tokens[self.i + 1] == ":"):
                start = self.take()
                self.take(":")
                end = self.take()
                if not re.fullmatch(r"[A-Z][1-9]\d?", end):
                    raise ValueError("invalid range")
                return ("range", start, end)
            return self.expression()

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parser = Parser(content[1:])
            parsed[name] = parser.expression()

    values = {}
    active = set()
    ERROR_DIV = "#DIV/0!"
    ERROR_CYCLE = "#CYCLE!"

    def ref_value(name):
        if name not in cells:
            return 0
        if name in active:
            return ERROR_CYCLE
        if name in values:
            return values[name]
        active.add(name)
        content = cells[name]
        if content.startswith("="):
            value = eval_node(parsed[name])
        else:
            value = int(content)
        active.remove(name)
        values[name] = value
        return value

    def is_error(value):
        return isinstance(value, str)

    def eval_node(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return ref_value(node[1])
        if kind == "neg":
            value = eval_node(node[1])
            return value if is_error(value) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
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
                return ERROR_DIV
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, left_node, op, right_node, yes_node, no_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left
            right = eval_node(right_node)
            if is_error(right):
                return right
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return eval_node(yes_node if condition else no_node)
        if kind == "func":
            _, name, args = node
            items = []
            for arg in args:
                if arg[0] == "range":
                    _, start, end = arg
                    c1, r1 = ord(start[0]) - 65, int(start[1:])
                    c2, r2 = ord(end[0]) - 65, int(end[1:])
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            cell = chr(col + 65) + str(row)
                            if cell in cells:
                                value = ref_value(cell)
                                if is_error(value):
                                    return value
                                items.append(value)
                else:
                    value = eval_node(arg)
                    if is_error(value):
                        return value
                    items.append(value)
            if name == "SUM":
                return sum(items)
            if not items:
                return 0
            return min(items) if name == "MIN" else max(items)
        raise ValueError("invalid node")

    for name in cells:
        ref_value(name)
    return {name: values[name] for name in cells}
