def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    token_re = re.compile(
        r"\s*(\d+|[A-Z][1-9]\d?|<>|<=|>=|[A-Z]+|[+\-*/(),:<>=])"
    )

    def is_cell(token):
        return (
            token is not None
            and len(token) in (2, 3)
            and "A" <= token[0] <= "Z"
            and token[1:].isdigit()
        )

    class Parser:
        def __init__(self, text):
            self.tokens = []
            pos = 0
            while pos < len(text):
                match = token_re.match(text, pos)
                if not match:
                    break
                self.tokens.append(match.group(1))
                pos = match.end()
            self.i = 0

        def peek(self, offset=0):
            j = self.i + offset
            return self.tokens[j] if j < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.i += 1
            return token

        def parse(self):
            return self.parse_add()

        def parse_add(self):
            node = self.parse_mul()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.parse_mul())
            return node

        def parse_mul(self):
            node = self.parse_unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("bin", op, node, self.parse_unary())
            return node

        def parse_unary(self):
            if self.peek() == "-":
                self.take()
                return ("neg", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            token = self.take()

            if token == "(":
                node = self.parse_add()
                self.take()  # ")"
                return node

            if token.isdigit():
                return int(token)

            if is_cell(token):
                return ("ref", token)

            if token in ("SUM", "MIN", "MAX"):
                self.take()  # "("
                args = [self.parse_argument()]
                while self.peek() == ",":
                    self.take()
                    args.append(self.parse_argument())
                self.take()  # ")"
                return ("func", token, args)

            if token == "IF":
                self.take()  # "("
                left = self.parse_add()
                op = self.take()
                right = self.parse_add()
                self.take()  # ","
                then_node = self.parse_add()
                self.take()  # ","
                else_node = self.parse_add()
                self.take()  # ")"
                return ("if", op, left, right, then_node, else_node)

            return 0

        def parse_argument(self):
            if is_cell(self.peek()) and self.peek(1) == ":":
                first = self.take()
                self.take()
                second = self.take()
                return ("range", first, second)
            return self.parse_add()

    parsed = {}
    state = {}
    values = {}

    def cell_coords(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return "#CYCLE!"
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        content = cells[name]

        if not content.startswith("="):
            value = int(content.strip())
        else:
            if name not in parsed:
                parsed[name] = Parser(content[1:]).parse()
            value = evaluate_node(parsed[name])

        values[name] = value
        state[name] = 2
        return value

    def evaluate_node(node):
        if isinstance(node, int):
            return node

        kind = node[0]

        if kind == "ref":
            return evaluate_cell(node[1])

        if kind == "neg":
            value = evaluate_node(node[1])
            return value if isinstance(value, str) else -value

        if kind == "bin":
            left = evaluate_node(node[2])
            if isinstance(left, str):
                return left

            right = evaluate_node(node[3])
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

        if kind == "range":
            x1, y1 = cell_coords(node[1])
            x2, y2 = cell_coords(node[2])
            total = []
            for row in range(min(y1, y2), max(y1, y2) + 1):
                for col in range(min(x1, x2), max(x1, x2) + 1):
                    cell_name = chr(ord("A") + col) + str(row + 1)
                    if cell_name in cells:
                        value = evaluate_cell(cell_name)
                        if isinstance(value, str):
                            return value
                        total.append(value)
            return total

        if kind == "func":
            name = node[1]
            collected = []

            for arg in node[2]:
                if arg[0] == "range":
                    values_in_arg = evaluate_node(arg)
                    if isinstance(values_in_arg, str):
                        return values_in_arg
                    collected.extend(values_in_arg)
                else:
                    value = evaluate_node(arg)
                    if isinstance(value, str):
                        return value
                    collected.append(value)

            if name == "SUM":
                return sum(collected)
            if not collected:
                return 0
            return min(collected) if name == "MIN" else max(collected)

        if kind == "if":
            left = evaluate_node(node[2])
            if isinstance(left, str):
                return left

            right = evaluate_node(node[3])
            if isinstance(right, str):
                return right

            op = node[1]
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

            return evaluate_node(node[4] if condition else node[5])

    return {name: evaluate_cell(name) for name in cells}
