def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    ERR_DIV = "#DIV/0!"
    ERR_CYCLE = "#CYCLE!"
    token_re = re.compile(r"(<=|>=|<>|[0-9]+|[A-Za-z]+[0-9]*|[()+\-*/,:=<>])")
    cell_re = re.compile(r"[A-Z][1-9][0-9]?")

    def is_cell(token):
        return token is not None and cell_re.fullmatch(token) is not None

    def tokenize(s):
        tokens = []
        pos = 0
        n = len(s)
        while True:
            while pos < n and s[pos].isspace():
                pos += 1
            if pos == n:
                return tokens
            match = token_re.match(s, pos)
            if match is None:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()

    class Parser:
        # Builds an AST without evaluating anything, so every token is always consumed.
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def peek(self, offset=0):
            i = self.pos + offset
            return self.tokens[i] if i < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.pos += 1
            return token

        def expect(self, token):
            if self.take() != token:
                raise ValueError(f"expected {token}")

        def formula(self):
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
                node = self.formula()
                self.expect(")")
                return node
            if token.isdigit():
                return ("num", int(token))
            if token in ("SUM", "MIN", "MAX"):
                return self.call(token)
            if token == "IF":
                return self.if_call()
            if is_cell(token):
                return ("ref", token)
            raise ValueError("Invalid atom")

        def call(self, fn):
            self.expect("(")
            args = []
            while True:
                if is_cell(self.peek()) and self.peek(1) == ":":
                    start = self.take()
                    self.take()  # :
                    end = self.take()
                    args.append(("range", start, end))
                else:
                    args.append(self.formula())
                if self.peek() == ",":
                    self.take()
                else:
                    break
            self.expect(")")
            return ("call", fn, args)

        def if_call(self):
            self.expect("(")
            left = self.formula()
            op = self.take()
            right = self.formula()
            self.expect(",")
            then_node = self.formula()
            self.expect(",")
            else_node = self.formula()
            self.expect(")")
            return ("if", left, op, right, then_node, else_node)

    asts = {}
    for name, content in cells.items():
        if content.startswith("="):
            asts[name] = Parser(tokenize(content[1:])).formula()

    def range_names(a, b):
        c1, r1 = ord(a[0]) - 65, int(a[1:])
        c2, r2 = ord(b[0]) - 65, int(b[1:])
        for row in range(min(r1, r2), max(r1, r2) + 1):
            for col in range(min(c1, c2), max(c1, c2) + 1):
                yield f"{chr(65 + col)}{row}"

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    def compare(left, op, right):
        if op == "=":
            return left == right
        if op == "<>":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        raise ValueError("Invalid comparison")

    def combine(fn, current, value):
        if current is None:
            return value
        if fn == "SUM":
            return current + value
        if fn == "MIN":
            return min(current, value)
        return max(current, value)

    values = {}
    active = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return ERR_CYCLE

        active.add(name)
        if name in asts:
            value = evaluate(asts[name])
        else:
            value = int(cells[name])
        active.discard(name)
        values[name] = value
        return value

    def call_function(node):
        _, fn, args = node
        result = None
        for arg in args:
            if arg[0] == "range":
                for name in range_names(arg[1], arg[2]):
                    if name not in cells:
                        continue
                    value = cell_value(name)
                    if isinstance(value, str):
                        return value
                    result = combine(fn, result, value)
            else:
                value = evaluate(arg)
                if isinstance(value, str):
                    return value
                result = combine(fn, result, value)
        return 0 if result is None else result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
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
                return ERR_DIV
            return trunc_div(left, right)
        if kind == "if":
            _, left_node, op, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            if compare(left, op, right):
                return evaluate(then_node)
            return evaluate(else_node)
        return call_function(node)

    return {name: cell_value(name) for name in cells}
