def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    total_size = sum(len(content) for content in cells.values())
    needed_limit = min(1_000_000, max(10_000, total_size * 4 + 10_000))
    if sys.getrecursionlimit() < needed_limit:
        sys.setrecursionlimit(needed_limit)

    token_re = re.compile(
        r"\s*(?:(\d+)|([A-Z][1-9]\d?|SUM|MIN|MAX|IF)|"
        r"(<>|<=|>=|[+\-*/(),:=<>]))"
    )

    def is_cell_name(token):
        return (
            isinstance(token, str)
            and 2 <= len(token) <= 3
            and "A" <= token[0] <= "Z"
            and token[1:].isdigit()
        )

    def tokenize(text):
        text = text.strip()
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(next(group for group in match.groups() if group is not None))
            pos = match.end()
        return tokens

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.pos = 0

        def peek(self, offset=0):
            index = self.pos + offset
            return self.tokens[index] if index < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if expected is not None and token != expected:
                raise ValueError("Invalid formula")
            self.pos += 1
            return token

        def parse(self):
            result = self.parse_add()
            if self.peek() is not None:
                raise ValueError("Invalid formula")
            return result

        def parse_add(self):
            node = self.parse_mul()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("binary", op, node, self.parse_mul())
            return node

        def parse_mul(self):
            node = self.parse_unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("binary", op, node, self.parse_unary())
            return node

        def parse_unary(self):
            if self.peek() == "-":
                self.take("-")
                return ("neg", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            token = self.take()

            if token.isdigit():
                return ("number", int(token))

            if is_cell_name(token):
                return ("cell", token)

            if token == "(":
                node = self.parse_add()
                self.take(")")
                return node

            if token == "IF":
                self.take("(")
                left = self.parse_add()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid comparison")
                right = self.parse_add()
                self.take(",")
                then_branch = self.parse_add()
                self.take(",")
                else_branch = self.parse_add()
                self.take(")")
                return ("if", op, left, right, then_branch, else_branch)

            if token in ("SUM", "MIN", "MAX"):
                self.take("(")
                args = []
                while True:
                    if is_cell_name(self.peek()) and self.peek(1) == ":":
                        first = self.take()
                        self.take(":")
                        second = self.take()
                        args.append(("range", first, second))
                    else:
                        args.append(("formula", self.parse_add()))

                    if self.peek() != ",":
                        break
                    self.take(",")

                self.take(")")
                return ("aggregate", token, args)

            raise ValueError("Invalid formula")

    state = {}
    values = {}
    parsed = {}

    def evaluate_cell(name):
        if name not in cells:
            return 0

        current_state = state.get(name, 0)
        if current_state == 2:
            return values[name]
        if current_state == 1:
            return "#CYCLE!"

        state[name] = 1
        content = cells[name]

        if not content.startswith("="):
            value = int(content)
        else:
            if name not in parsed:
                parsed[name] = Parser(content[1:]).parse()
            value = evaluate(parsed[name])

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
            _, op, left_node, right_node = node

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
                return "#DIV/0!"

            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node

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

        _, function, args = node
        found = False
        result = 0

        def include(value):
            nonlocal found, result
            if not found:
                result = value
                found = True
            elif function == "SUM":
                result += value
            elif function == "MIN":
                result = min(result, value)
            else:
                result = max(result, value)

        for argument in args:
            if argument[0] == "formula":
                value = evaluate(argument[1])
                if isinstance(value, str):
                    return value
                include(value)
                continue

            _, first, second = argument
            col1, row1 = ord(first[0]), int(first[1:])
            col2, row2 = ord(second[0]), int(second[1:])
            left_col, right_col = sorted((col1, col2))
            top_row, bottom_row = sorted((row1, row2))

            for row in range(top_row, bottom_row + 1):
                for col in range(left_col, right_col + 1):
                    name = chr(col) + str(row)
                    if name not in cells:
                        continue
                    value = evaluate_cell(name)
                    if isinstance(value, str):
                        return value
                    include(value)

        return result if found else 0

    return {name: evaluate_cell(name) for name in cells}
