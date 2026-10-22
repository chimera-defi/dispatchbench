def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 30000))

    token_re = re.compile(r"\s*(<=|>=|<>|[()+\-*/,=:<>]|[A-Z][0-9]+|\d+)")
    name_re = re.compile(r"([A-Z])(\d+)")

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                if text[pos:].strip() == "":
                    break
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.i += 1
            return token

        def parse(self):
            return self.expression()

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
                self.take()  # )
                return node
            if token is None:
                raise ValueError("Unexpected end of formula")
            if token.isdigit():
                return ("num", int(token))
            if token in ("SUM", "MIN", "MAX", "IF"):
                self.take()  # (
                if token == "IF":
                    left = self.expression()
                    op = self.take()
                    right = self.expression()
                    self.take()  # ,
                    then_node = self.expression()
                    self.take()  # ,
                    else_node = self.expression()
                    self.take()  # )
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    first = self.peek()
                    second = self.tokens[self.i + 1] if self.i + 1 < len(self.tokens) else None
                    third = self.tokens[self.i + 2] if self.i + 2 < len(self.tokens) else None
                    if first and name_re.fullmatch(first) and second == ":" and third and name_re.fullmatch(third):
                        a = self.take()
                        self.take()
                        b = self.take()
                        args.append(("range", a, b))
                    else:
                        args.append(self.expression())
                    if self.peek() != ",":
                        break
                    self.take()
                self.take()  # )
                return ("func", token, args)
            return ("ref", token)

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = Parser(tokenize(content[1:])).parse()
        else:
            parsed[name] = int(content)

    values = {}
    state = {}

    def coords(name):
        match = name_re.fullmatch(name)
        return ord(match.group(1)) - ord("A"), int(match.group(2))

    def eval_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return "#CYCLE!"
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        content = parsed[name]
        value = content if isinstance(content, int) else eval_node(content)
        values[name] = value
        state[name] = 2
        return value

    def eval_node(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
        if kind == "neg":
            value = eval_node(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = eval_node(left_node)
            if isinstance(left, str):
                return left
            right = eval_node(right_node)
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
            left = eval_node(left_node)
            if isinstance(left, str):
                return left
            right = eval_node(right_node)
            if isinstance(right, str):
                return right
            tests = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return eval_node(then_node if tests[op] else else_node)

        _, func, args = node
        collected = []
        for arg in args:
            if arg[0] == "range":
                _, first, last = arg
                col1, row1 = coords(first)
                col2, row2 = coords(last)
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        name = chr(ord("A") + col) + str(row)
                        if name in cells:
                            value = eval_cell(name)
                            if isinstance(value, str):
                                return value
                            collected.append(value)
            else:
                value = eval_node(arg)
                if isinstance(value, str):
                    return value
                collected.append(value)

        if not collected:
            return 0
        if func == "SUM":
            return sum(collected)
        if func == "MIN":
            return min(collected)
        return max(collected)

    return {name: eval_cell(name) for name in cells}
