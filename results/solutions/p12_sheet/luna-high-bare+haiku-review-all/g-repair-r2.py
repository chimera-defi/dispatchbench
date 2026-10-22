import re
import sys


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 50000))

    token_re = re.compile(
        r"\s*(<=|>=|<>|[A-Z](?:[1-9]\d?)|\d+|[A-Za-z_]+|[()+*/,.:<>=-])"
    )

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.i += 1
            return token

        def parse_expr(self):
            node = self.parse_term()
            while self.peek() in ("+", "-"):
                op = self.take()
                node = ("bin", op, node, self.parse_term())
            return node

        def parse_term(self):
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
                node = self.parse_expr()
                self.take()  # )
                return node
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                return ("num", int(token))
            if re.fullmatch(r"[A-Z][1-9]\d?", token):
                return ("ref", token)
            if token in ("SUM", "MIN", "MAX", "IF"):
                self.take()  # (
                if token == "IF":
                    left = self.parse_expr()
                    op = self.take()
                    right = self.parse_expr()
                    self.take()  # ,
                    then_node = self.parse_expr()
                    self.take()  # ,
                    else_node = self.parse_expr()
                    self.take()  # )
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    first = self.peek()
                    if (
                        first is not None
                        and re.fullmatch(r"[A-Z][1-9]\d?", first)
                        and self.i + 1 < len(self.tokens)
                        and self.tokens[self.i + 1] == ":"
                    ):
                        start = self.take()
                        self.take()  # :
                        end = self.take()
                        args.append(("range", start, end))
                    else:
                        args.append(("expr", self.parse_expr()))
                    if self.peek() == ",":
                        self.take()
                    else:
                        break
                self.take()  # )
                return ("func", token, args)
            raise ValueError("Invalid formula")

    parsed = {}
    for name, content in cells.items():
        if isinstance(content, int):
            parsed[name] = ("num", content)
        else:
            text = str(content).strip()
            if text.startswith("="):
                parsed[name] = Parser(text[1:]).parse_expr()
            else:
                parsed[name] = ("num", int(text))

    values = {}
    active = set()

    def coordinates(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def get_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return "#CYCLE!"
        active.add(name)
        value = evaluate(parsed[name])
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
            matches = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(then_node if matches else else_node)

        _, function, args = node
        collected = []
        for arg in args:
            if arg[0] == "expr":
                value = evaluate(arg[1])
                if isinstance(value, str):
                    return value
                collected.append(value)
            else:
                _, start, end = arg
                c1, r1 = coordinates(start)
                c2, r2 = coordinates(end)
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        name = chr(ord("A") + col) + str(row)
                        if name in cells:
                            value = get_cell(name)
                            if isinstance(value, str):
                                return value
                            collected.append(value)

        if function == "SUM":
            return sum(collected)
        if not collected:
            return 0
        return min(collected) if function == "MIN" else max(collected)

    for name in cells:
        get_cell(name)
    return values
