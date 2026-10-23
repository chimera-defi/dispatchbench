def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    state: dict[str, int] = {}
    values: dict[str, int | str] = {}

    def is_error(value):
        return isinstance(value, str)

    def is_cell_token(token):
        return (
            len(token) >= 2
            and "A" <= token[0] <= "Z"
            and token[1:].isdigit()
        )

    def tokenize(text):
        tokens = []
        i = 0

        while i < len(text):
            c = text[i]

            if c.isspace():
                i += 1
            elif c.isdigit():
                j = i
                while j < len(text) and text[j].isdigit():
                    j += 1
                tokens.append(text[i:j])
                i = j
            elif c.isupper():
                j = i
                while j < len(text) and text[j].isupper():
                    j += 1
                k = j
                while k < len(text) and text[k].isdigit():
                    k += 1
                tokens.append(text[i:k])
                i = k
            elif c in "<>":
                if i + 1 < len(text) and text[i + 1] in "= >".replace(" ", ""):
                    tokens.append(text[i:i + 2])
                    i += 2
                else:
                    tokens.append(c)
                    i += 1
            else:
                tokens.append(c)
                i += 1

        return tokens

    def eval_cell(name):
        if name not in cells:
            return 0

        if state.get(name) == 1:
            return CYCLE
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        content = cells[name].strip()

        if content.startswith("="):
            value = Parser(tokenize(content[1:])).parse()
        else:
            value = int(content)

        state[name] = 2
        values[name] = value
        return value

    def apply_binary(left, op, right):
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if right == 0:
            return DIV0
        result = abs(left) // abs(right)
        return -result if (left < 0) != (right < 0) else result

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def peek(self, offset=0):
            index = self.pos + offset
            return self.tokens[index] if index < len(self.tokens) else None

        def take(self, expected=None):
            token = self.peek()
            if expected is not None and token != expected:
                raise ValueError("invalid formula")
            self.pos += 1
            return token

        def parse(self):
            return self.parse_expr(True)

        def parse_expr(self, run):
            value = self.parse_term(run)

            while self.peek() in ("+", "-"):
                op = self.take()
                if run and is_error(value):
                    self.parse_term(False)
                else:
                    right = self.parse_term(run)
                    if run:
                        value = apply_binary(value, op, right)

            return value if run else 0

        def parse_term(self, run):
            value = self.parse_unary(run)

            while self.peek() in ("*", "/"):
                op = self.take()
                if run and is_error(value):
                    self.parse_unary(False)
                else:
                    right = self.parse_unary(run)
                    if run:
                        value = apply_binary(value, op, right)

            return value if run else 0

        def parse_unary(self, run):
            if self.peek() == "-":
                self.take("-")
                value = self.parse_unary(run)
                return -value if run and not is_error(value) else (
                    value if run else 0
                )

            return self.parse_atom(run)

        def parse_atom(self, run):
            token = self.take()

            if token == "(":
                value = self.parse_expr(run)
                self.take(")")
                return value if run else 0

            if token.isdigit():
                return int(token) if run else 0

            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.parse_function(token, run)

            return eval_cell(token) if run else 0

        def parse_function(self, name, run):
            self.take("(")

            if name == "IF":
                left = self.parse_expr(run)
                op = self.take()

                left_error = run and is_error(left)
                right = self.parse_expr(False if left_error else run)
                self.take(",")

                if not run:
                    self.parse_expr(False)
                    self.take(",")
                    self.parse_expr(False)
                    self.take(")")
                    return 0

                if left_error:
                    self.parse_expr(False)
                    self.take(",")
                    self.parse_expr(False)
                    self.take(")")
                    return left

                if is_error(right):
                    self.parse_expr(False)
                    self.take(",")
                    self.parse_expr(False)
                    self.take(")")
                    return right

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

                then_value = self.parse_expr(condition)
                self.take(",")
                else_value = self.parse_expr(not condition)
                self.take(")")

                return then_value if condition else else_value

            aggregate = []
            first_error = None

            while True:
                arg_run = run and first_error is None

                if is_cell_token(self.peek()) and self.peek(1) == ":":
                    start = self.take()
                    self.take(":")
                    end = self.take()

                    if arg_run:
                        c1 = ord(start[0]) - ord("A")
                        r1 = int(start[1:]) - 1
                        c2 = ord(end[0]) - ord("A")
                        r2 = int(end[1:]) - 1

                        lo_r, hi_r = sorted((r1, r2))
                        lo_c, hi_c = sorted((c1, c2))

                        for r in range(lo_r, hi_r + 1):
                            for c in range(lo_c, hi_c + 1):
                                cell_name = chr(ord("A") + c) + str(r + 1)
                                if cell_name in cells:
                                    value = eval_cell(cell_name)
                                    if is_error(value):
                                        first_error = value
                                        break
                                    aggregate.append(value)
                            if first_error is not None:
                                break
                else:
                    value = self.parse_expr(arg_run)
                    if arg_run:
                        if is_error(value):
                            first_error = value
                        else:
                            aggregate.append(value)

                if self.peek() != ",":
                    break
                self.take(",")

            self.take(")")

            if not run:
                return 0
            if first_error is not None:
                return first_error
            if not aggregate:
                return 0

            if name == "SUM":
                return sum(aggregate)
            if name == "MIN":
                return min(aggregate)
            return max(aggregate)

    for name in cells:
        eval_cell(name)

    return values
