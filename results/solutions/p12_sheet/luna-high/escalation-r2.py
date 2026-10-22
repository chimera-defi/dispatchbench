def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    token_re = re.compile(r"\s*(<>|<=|>=|[A-Z]+[0-9]*|\d+|[+\-*/(),:<>=])")
    parsed = {}

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                pos += 1
                continue
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if expected is not None and token != expected:
                raise ValueError("Invalid formula")
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
            token = self.peek()
            if token == "(":
                self.take()
                node = self.expression()
                self.take(")")
                return node
            if token is not None and token.isdigit():
                self.take()
                return ("num", int(token))
            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.function()
            if token is not None and re.fullmatch(r"[A-Z][1-9][0-9]?", token):
                self.take()
                return ("ref", token)
            raise ValueError("Invalid formula")

        def function(self):
            name = self.take()
            self.take("(")
            if name == "IF":
                left = self.expression()
                op = self.take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid formula")
                right = self.expression()
                self.take(",")
                then_node = self.expression()
                self.take(",")
                else_node = self.expression()
                self.take(")")
                return ("if", op, left, right, then_node, else_node)

            args = []
            while True:
                first = self.peek()
                second = self.tokens[self.i + 1] if self.i + 1 < len(self.tokens) else None
                third = self.tokens[self.i + 2] if self.i + 2 < len(self.tokens) else None
                if (first is not None and re.fullmatch(r"[A-Z][1-9][0-9]?", first)
                        and second == ":"
                        and third is not None
                        and re.fullmatch(r"[A-Z][1-9][0-9]?", third)):
                    start = self.take()
                    self.take(":")
                    end = self.take()
                    args.append(("range", start, end))
                else:
                    args.append(("formula", self.expression()))
                if self.peek() != ",":
                    break
                self.take(",")
            self.take(")")
            return ("func", name, args)

    for name, content in cells.items():
        if content.startswith("="):
            parser = Parser(tokenize(content[1:]))
            parsed[name] = parser.expression()
        else:
            parsed[name] = ("num", int(content))

    cache = {}
    in_progress = set()
    errors = {"#DIV/0!", "#CYCLE!"}

    def cell_value(name):
        if name not in cells:
            return 0
        if name in cache:
            return cache[name]
        if name in in_progress:
            return "#CYCLE!"
        in_progress.add(name)
        result = evaluate(parsed[name])
        in_progress.remove(name)
        cache[name] = result
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if value in errors else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if left in errors:
                return left
            right = evaluate(right_node)
            if right in errors:
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
            if left in errors:
                return left
            right = evaluate(right_node)
            if right in errors:
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

        _, name, args = node
        values = []
        for arg in args:
            if arg[0] == "formula":
                value = evaluate(arg[1])
                if value in errors:
                    return value
                values.append(value)
            else:
                _, start, end = arg
                c1, r1 = ord(start[0]) - ord("A"), int(start[1:])
                c2, r2 = ord(end[0]) - ord("A"), int(end[1:])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell = chr(ord("A") + col) + str(row)
                        if cell in cells:
                            value = cell_value(cell)
                            if value in errors:
                                return value
                            values.append(value)

        if name == "SUM":
            return sum(values)
        if not values:
            return 0
        return min(values) if name == "MIN" else max(values)

    return {name: cell_value(name) for name in cells}
