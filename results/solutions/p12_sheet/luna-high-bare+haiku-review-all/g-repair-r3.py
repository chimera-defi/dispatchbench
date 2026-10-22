import re
import sys

def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(20000)

    token_re = re.compile(r"\d+|[A-Za-z]+[0-9]+|[A-Za-z]+|<>|<=|>=|[+\-*/(),:=<>]")

    def tokenize(text):
        return token_re.findall(text)

    def col_row(name):
        return ord(name[0]) - ord("A"), int(name[1:])

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
            if token.isdigit():
                return ("num", int(token))
            if re.fullmatch(r"[A-Z][0-9]+", token):
                return ("ref", token)

            name = token
            self.take()  # (
            if name == "IF":
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
            while self.peek() != ")":
                if (self.peek() and re.fullmatch(r"[A-Z][0-9]+", self.peek())
                        and self.i + 1 < len(self.tokens)
                        and self.tokens[self.i + 1] == ":"):
                    start = self.take()
                    self.take()  # :
                    end = self.take()
                    args.append(("range", start, end))
                else:
                    args.append(("formula", self.parse_expr()))
                if self.peek() == ",":
                    self.take()
                else:
                    break
            self.take()  # )
            return ("func", name, args)

    cache = {}
    visiting = set()

    def is_error(value):
        return isinstance(value, str) and value.startswith("#")

    def eval_node(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
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
                return "#DIV/0!"
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left
            right = eval_node(right_node)
            if is_error(right):
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

        _, name, args = node
        values = []
        for arg in args:
            if arg[0] == "formula":
                value = eval_node(arg[1])
                if is_error(value):
                    return value
                values.append(value)
            else:
                _, start, end = arg
                c1, r1 = col_row(start)
                c2, r2 = col_row(end)
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell = chr(ord("A") + col) + str(row)
                        if cell in cells:
                            value = eval_cell(cell)
                            if is_error(value):
                                return value
                            values.append(value)

        if name == "SUM":
            return sum(values)
        if not values:
            return 0
        return min(values) if name == "MIN" else max(values)

    def eval_cell(name):
        if name not in cells:
            return 0
        if name in cache:
            return cache[name]
        if name in visiting:
            return "#CYCLE!"
        visiting.add(name)
        content = cells[name].strip()
        if content.startswith("="):
            value = eval_node(Parser(tokenize(content[1:])).parse_expr())
        else:
            value = int(content)
        visiting.remove(name)
        cache[name] = value
        return value

    return {name: eval_cell(name) for name in cells}
