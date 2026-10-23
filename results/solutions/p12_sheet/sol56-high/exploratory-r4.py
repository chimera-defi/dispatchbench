def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))

    DIV_ZERO = "#DIV/0!"
    CYCLE = "#CYCLE!"

    class Parser:
        def __init__(self, text):
            self.tokens = self.tokenize(text)
            self.pos = 0

        @staticmethod
        def tokenize(text):
            tokens = []
            i = 0
            while i < len(text):
                if text[i].isspace():
                    i += 1
                elif text[i].isdigit():
                    j = i + 1
                    while j < len(text) and text[j].isdigit():
                        j += 1
                    tokens.append(text[i:j])
                    i = j
                elif text[i].isalpha():
                    j = i + 1
                    while j < len(text) and text[j].isalnum():
                        j += 1
                    tokens.append(text[i:j])
                    i = j
                elif text.startswith(("<=", ">=", "<>"), i):
                    tokens.append(text[i:i + 2])
                    i += 2
                else:
                    tokens.append(text[i])
                    i += 1
            tokens.append(None)
            return tokens

        def peek(self, offset=0):
            return self.tokens[self.pos + offset]

        def take(self, expected=None):
            token = self.tokens[self.pos]
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
            negate = False
            while self.peek() == "-":
                self.take("-")
                negate = not negate
            node = self.parse_atom()
            return ("neg", node) if negate else node

        def parse_atom(self):
            token = self.peek()

            if token.isdigit():
                self.take()
                return ("number", int(token))

            if token == "(":
                self.take("(")
                node = self.parse_add()
                self.take(")")
                return node

            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.parse_call()

            self.take()
            return ("reference", token)

        def parse_call(self):
            name = self.take()
            self.take("(")

            if name == "IF":
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

            arguments = []
            while True:
                if (
                    self.peek() is not None
                    and len(self.peek()) >= 2
                    and self.peek()[0].isalpha()
                    and self.peek()[1:].isdigit()
                    and self.peek(1) == ":"
                ):
                    start = self.take()
                    self.take(":")
                    end = self.take()
                    arguments.append(("range", start, end))
                else:
                    arguments.append(self.parse_add())

                if self.peek() != ",":
                    break
                self.take(",")

            self.take(")")
            return ("function", name, arguments)

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = Parser(content[1:]).parse()
        else:
            parsed[name] = ("number", int(content))

    values = {}
    state = {}

    def is_error(value):
        return isinstance(value, str)

    def evaluate_cell(name):
        if name not in parsed:
            return 0
        if state.get(name) == 1:
            return CYCLE
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        value = evaluate(parsed[name])
        values[name] = value
        state[name] = 2
        return value

    def evaluate(node):
        kind = node[0]

        if kind == "number":
            return node[1]

        if kind == "reference":
            return evaluate_cell(node[1])

        if kind == "neg":
            value = evaluate(node[1])
            return value if is_error(value) else -value

        if kind == "binary":
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
                return DIV_ZERO

            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node

            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
            if is_error(right):
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

        _, function_name, arguments = node
        result = None

        def include(value):
            nonlocal result
            if function_name == "SUM":
                result = (0 if result is None else result) + value
            elif result is None:
                result = value
            elif function_name == "MIN":
                result = min(result, value)
            else:
                result = max(result, value)

        for argument in arguments:
            if argument[0] != "range":
                value = evaluate(argument)
                if is_error(value):
                    return value
                include(value)
                continue

            start, end = argument[1], argument[2]
            col1, row1 = ord(start[0]), int(start[1:])
            col2, row2 = ord(end[0]), int(end[1:])

            first_col, last_col = sorted((col1, col2))
            first_row, last_row = sorted((row1, row2))

            for row in range(first_row, last_row + 1):
                for col in range(first_col, last_col + 1):
                    cell_name = chr(col) + str(row)
                    if cell_name not in cells:
                        continue
                    value = evaluate_cell(cell_name)
                    if is_error(value):
                        return value
                    include(value)

        return 0 if result is None else result

    return {name: evaluate_cell(name) for name in cells}
