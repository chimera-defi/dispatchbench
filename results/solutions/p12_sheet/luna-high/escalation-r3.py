def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(100000)

    error_div = "#DIV/0!"
    error_cycle = "#CYCLE!"
    tokens_re = re.compile(r"[A-Z][1-9]\d?|[A-Z]+|\d+|<>|<=|>=|[+\-*/(),:=<>]")

    class Parser:
        def __init__(self, text):
            self.tokens = tokens_re.findall(text)
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def take(self):
            token = self.peek()
            if token is None:
                raise ValueError("Unexpected end of formula")
            self.pos += 1
            return token

        def parse(self):
            result = self.parse_add()
            if self.peek() is not None:
                raise ValueError("Unexpected token")
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
                self.take()
                return ("neg", self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            token = self.take()

            if token == "(":
                node = self.parse_add()
                self.take()  # )
                return node

            if token.isdigit():
                return ("literal", int(token))

            if re.fullmatch(r"[A-Z][1-9]\d?", token):
                return ("cell", token)

            if token in ("SUM", "MIN", "MAX", "IF"):
                self.take()  # (
                if token == "IF":
                    left = self.parse_add()
                    op = self.take()
                    right = self.parse_add()
                    self.take()  # ,
                    then_node = self.parse_add()
                    self.take()  # ,
                    else_node = self.parse_add()
                    self.take()  # )
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    first = self.peek()
                    second = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                    if first is not None and re.fullmatch(r"[A-Z][1-9]\d?", first) and second == ":":
                        start = self.take()
                        self.take()  # :
                        end = self.take()
                        args.append(("range", start, end))
                    else:
                        args.append(("formula_arg", self.parse_add()))

                    if self.peek() == ")":
                        self.take()
                        break
                    self.take()  # ,
                return ("func", token, args)

            raise ValueError("Invalid formula atom")

    values = {}
    state = {}

    def coords(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def evaluate_node(node):
        kind = node[0]

        if kind == "literal":
            return node[1]
        if kind == "cell":
            return evaluate_cell(node[1])
        if kind == "neg":
            value = evaluate_node(node[1])
            return value if isinstance(value, str) else -value

        if kind == "binary":
            _, op, left_node, right_node = node
            left = evaluate_node(left_node)
            if isinstance(left, str):
                return left
            right = evaluate_node(right_node)
            if isinstance(right, str):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return error_div
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = evaluate_node(left_node)
            if isinstance(left, str):
                return left
            right = evaluate_node(right_node)
            if isinstance(right, str):
                return right

            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate_node(then_node if comparisons[op] else else_node)

        if kind == "func":
            _, name, args = node
            collected = []
            for arg in args:
                if arg[0] == "formula_arg":
                    value = evaluate_node(arg[1])
                    if isinstance(value, str):
                        return value
                    collected.append(value)
                else:
                    _, start, end = arg
                    col1, row1 = coords(start)
                    col2, row2 = coords(end)
                    for row in range(min(row1, row2), max(row1, row2) + 1):
                        for col in range(min(col1, col2), max(col1, col2) + 1):
                            cell_name = chr(ord("A") + col) + str(row)
                            if cell_name in cells:
                                value = evaluate_cell(cell_name)
                                if isinstance(value, str):
                                    return value
                                collected.append(value)

            if not collected:
                return 0
            if name == "SUM":
                return sum(collected)
            if name == "MIN":
                return min(collected)
            return max(collected)

        raise ValueError("Invalid node")

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return error_cycle
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        content = cells[name]
        if content.startswith("="):
            result = evaluate_node(Parser(content[1:]).parse())
        else:
            result = int(content)
        values[name] = result
        state[name] = 2
        return result

    for cell_name in cells:
        evaluate_cell(cell_name)

    return values
