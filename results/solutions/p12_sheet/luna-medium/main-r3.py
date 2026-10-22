def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    # Tokenize formulas, keeping cell names and function names intact.
    token_re = re.compile(
        r"\s*(<=|>=|<>|[+\-*/(),:=<>]|[A-Za-z]+[1-9][0-9]?|[A-Za-z]+|[0-9]+)"
    )

    class Parser:
        def __init__(self, text):
            self.tokens = [m.group(1) for m in token_re.finditer(text)]
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
            token = self.take()
            if token == "(":
                node = self.expression()
                self.take(")")
                return node
            if token.isdigit():
                return ("num", int(token))
            if token and token[0].isalpha() and token[1:].isdigit():
                return ("ref", token)

            name = token.upper()
            self.take("(")
            if name == "IF":
                left = self.expression()
                op = self.take()
                right = self.expression()
                self.take(",")
                yes = self.expression()
                self.take(",")
                no = self.expression()
                self.take(")")
                return ("if", left, op, right, yes, no)

            args = []
            while True:
                first = self.expression()
                if self.peek() == ":":
                    self.take(":")
                    second = self.expression()
                    args.append(("range", first, second))
                else:
                    args.append(("expr", first))
                if self.peek() != ",":
                    break
                self.take(",")
            self.take(")")
            return ("func", name, args)

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = Parser(content[1:]).expression()
        else:
            parsed[name] = int(content)

    state = {}  # 0 absent, 1 evaluating, 2 finished
    values = {}
    stack = []

    def cell_value(name):
        if name not in parsed:
            return 0
        status = state.get(name, 0)
        if status == 1:
            # Mark every cell in the active dependency cycle. This ensures
            # cycle errors propagate even if an enclosing formula later
            # encounters a back-reference.
            try:
                start = stack.index(name)
                for member in stack[start:]:
                    values[member] = CYCLE
                    state[member] = 2
            except ValueError:
                pass
            return CYCLE
        if status == 2:
            return values[name]

        state[name] = 1
        stack.append(name)
        content = parsed[name]
        value = content if isinstance(content, int) else eval_node(content)
        stack.pop()
        if state.get(name) != 2:
            values[name] = value
            state[name] = 2
        return values[name]

    def eval_node(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            value = eval_node(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            left = eval_node(node[2])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
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
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            left = eval_node(node[1])
            if isinstance(left, str):
                return left
            right = eval_node(node[3])
            if isinstance(right, str):
                return right
            op = node[2]
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return eval_node(node[4] if condition else node[5])

        _, name, args = node
        collected = []
        for arg_kind, first, *rest in args:
            if arg_kind == "expr":
                value = eval_node(first)
                if isinstance(value, str):
                    return value
                collected.append(value)
            else:
                a = first
                b = rest[0]
                if a[0] != "ref" or b[0] != "ref":
                    continue
                c1, r1 = a[1][0], int(a[1][1:])
                c2, r2 = b[1][0], int(b[1][1:])
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(ord(min(c1, c2)), ord(max(c1, c2)) + 1):
                        ref = chr(col) + str(row)
                        if ref not in parsed:
                            continue
                        value = cell_value(ref)
                        if isinstance(value, str):
                            return value
                        collected.append(value)

        if name == "SUM":
            return sum(collected)
        if not collected:
            return 0
        if name == "MIN":
            return min(collected)
        return max(collected)

    result = {}
    for name in cells:
        result[name] = cell_value(name)
    return result
