def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    ERROR_DIV = "#DIV/0!"
    ERROR_CYCLE = "#CYCLE!"
    values = {}
    in_progress = set()

    token_re = re.compile(
        r"(?:(\d+)|([A-Z][1-9]\d?(?![A-Za-z0-9]))|([A-Z]+)|(<=|>=|<>|[+\-*/(),:=<>]))"
    )

    class Parser:
        def __init__(self, text):
            self.tokens = []
            pos = 0
            while pos < len(text):
                if text[pos].isspace():
                    pos += 1
                    continue
                match = token_re.match(text, pos)
                if not match:
                    raise ValueError("Invalid formula")
                self.tokens.append(next(g for g in match.groups() if g is not None))
                pos = match.end()
            self.index = 0

        def peek(self):
            return self.tokens[self.index] if self.index < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            self.index += 1
            return token

        def parse_formula(self):
            return self.parse_add()

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
            token = self.peek()
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                self.take()
                return ("number", int(token))
            if token == "(":
                self.take("(")
                node = self.parse_formula()
                self.take(")")
                return node
            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.parse_call()
            if re.fullmatch(r"[A-Z][1-9]\d?", token):
                self.take()
                return ("reference", token)
            raise ValueError("Invalid formula")

        def parse_call(self):
            name = self.take()
            self.take("(")
            if name == "IF":
                left = self.parse_formula()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid formula")
                right = self.parse_formula()
                self.take(",")
                then_node = self.parse_formula()
                self.take(",")
                else_node = self.parse_formula()
                self.take(")")
                return ("if", op, left, right, then_node, else_node)

            args = []
            while True:
                first = self.parse_formula()
                if self.peek() == ":":
                    self.take(":")
                    second = self.parse_formula()
                    if first[0] != "reference" or second[0] != "reference":
                        raise ValueError("Invalid formula")
                    args.append(("range", first[1], second[1]))
                else:
                    args.append(("argument", first))
                if self.peek() != ",":
                    break
                self.take(",")
            self.take(")")
            return ("function", name, args)

    def parse_cell_name(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in in_progress:
            return ERROR_CYCLE

        in_progress.add(name)
        content = cells[name]
        if isinstance(content, int):
            result = content
        else:
            text = content.strip()
            if text.startswith("="):
                parser = Parser(text[1:])
                tree = parser.parse_formula()
                if parser.peek() is not None:
                    raise ValueError("Invalid formula")
                result = evaluate(tree)
            else:
                result = int(text)
        in_progress.remove(name)
        values[name] = result
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "number":
            return node[1]
        if kind == "reference":
            return evaluate_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind == "binary":
            op, left_node, right_node = node[1:]
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
                return ERROR_DIV
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            op, left_node, right_node, then_node, else_node = node[1:]
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(then_node if condition else else_node)
        if kind == "function":
            name, args = node[1:]
            collected = []
            for arg in args:
                if arg[0] == "argument":
                    value = evaluate(arg[1])
                    if isinstance(value, str):
                        return value
                    collected.append(value)
                else:
                    _, first, second = arg
                    col1, row1 = parse_cell_name(first)
                    col2, row2 = parse_cell_name(second)
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
        raise ValueError("Invalid formula")

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 100000))
    try:
        for cell_name in cells:
            evaluate_cell(cell_name)
    finally:
        sys.setrecursionlimit(old_limit)
    return {name: values[name] for name in cells}
