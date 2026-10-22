def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    # Tokenize formulas, including multi-character comparison operators.
    token_re = re.compile(
        r"\s+|<=|>=|<>|[A-Za-z]+|\d+|[+\-*/(),:=<>]"
    )

    def tokenize(text):
        result = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if match is None:
                raise ValueError("Invalid formula")
            token = match.group()
            pos = match.end()
            if not token.isspace():
                result.append(token)
        return result

    def cell_pos(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    def cell_name(col, row):
        return chr(ord("A") + col) + str(row + 1)

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self):
            token = self.peek()
            if token is None:
                raise ValueError("Unexpected end of formula")
            self.i += 1
            return token

        def accept(self, token):
            if self.peek() == token:
                self.i += 1
                return True
            return False

        def parse(self):
            node = self.expression()
            if self.peek() is not None:
                raise ValueError("Unexpected token")
            return node

        def expression(self):
            node = self.product()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.product())
            return node

        def product(self):
            node = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.accept("-"):
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            token = self.take()
            if token == "(":
                node = self.expression()
                self.take()  # )
                return node

            if token.isdigit():
                return ("num", int(token))

            if token in ("SUM", "MIN", "MAX"):
                self.take()  # (
                args = []
                while True:
                    # A range begins with a cell name followed by ':'.
                    if (
                        self.peek() is not None
                        and re.fullmatch(r"[A-Z][1-9]\d?", self.peek())
                        and self.i + 1 < len(self.tokens)
                        and self.tokens[self.i + 1] == ":"
                    ):
                        start = self.take()
                        self.take()
                        end = self.take()
                        args.append(("range", start, end))
                    else:
                        args.append(self.expression())
                    if not self.accept(","):
                        break
                self.take()  # )
                return ("func", token, args)

            if token == "IF":
                self.take()  # (
                left = self.expression()
                op = self.take()
                right = self.expression()
                self.take()  # ,
                then_node = self.expression()
                self.take()  # ,
                else_node = self.expression()
                self.take()  # )
                return ("if", left, op, right, then_node, else_node)

            if re.fullmatch(r"[A-Z][1-9]\d?", token):
                return ("ref", token)

            raise ValueError("Invalid atom")

    trees = {}
    for name, content in cells.items():
        if content.startswith("="):
            trees[name] = Parser(tokenize(content[1:])).parse()

    state = {}
    values = {}

    def evaluate_cell(name):
        if name not in cells:
            return 0
        status = state.get(name, 0)
        if status == 1:
            return CYCLE
        if status == 2:
            return values[name]

        state[name] = 1
        content = cells[name]
        if content.startswith("="):
            value = evaluate(trees[name])
        else:
            value = int(content)
        values[name] = value
        state[name] = 2
        return value

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return evaluate_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
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
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            _, left_node, op, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
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
            return evaluate(then_node if comparisons[op] else else_node)

        if kind == "func":
            _, func, args = node
            aggregate = []
            for arg in args:
                if arg[0] == "range":
                    _, first, last = arg
                    c1, r1 = cell_pos(first)
                    c2, r2 = cell_pos(last)
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = cell_name(col, row)
                            if name in cells:
                                value = evaluate_cell(name)
                                if isinstance(value, str):
                                    return value
                                aggregate.append(value)
                else:
                    value = evaluate(arg)
                    if isinstance(value, str):
                        return value
                    aggregate.append(value)
            if not aggregate:
                return 0
            if func == "SUM":
                return sum(aggregate)
            if func == "MIN":
                return min(aggregate)
            return max(aggregate)

        raise ValueError("Invalid expression")

    return {name: evaluate_cell(name) for name in cells}
