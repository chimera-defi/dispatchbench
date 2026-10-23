def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(
        max(sys.getrecursionlimit(), 10000 + sum(map(len, cells.values())) * 2)
    )

    DIV_ZERO = "#DIV/0!"
    CYCLE = "#CYCLE!"
    ERRORS = {DIV_ZERO, CYCLE}

    def tokenize(text):
        tokens = []
        i = 0
        n = len(text)

        while i < n:
            c = text[i]
            if c.isspace():
                i += 1
            elif c.isdigit():
                j = i + 1
                while j < n and text[j].isdigit():
                    j += 1
                tokens.append(("NUM", int(text[i:j])))
                i = j
            elif c.isalpha():
                j = i + 1
                while j < n and (text[j].isalpha() or text[j].isdigit()):
                    j += 1
                word = text[i:j]
                if (
                    len(word) >= 2
                    and len(word) <= 3
                    and "A" <= word[0] <= "Z"
                    and word[1:].isdigit()
                ):
                    tokens.append(("CELL", word))
                else:
                    tokens.append(("NAME", word))
                i = j
            elif i + 1 < n and text[i:i + 2] in ("<>", "<=", ">="):
                tokens.append((text[i:i + 2], text[i:i + 2]))
                i += 2
            else:
                tokens.append((c, c))
                i += 1

        tokens.append(("EOF", None))
        return tokens

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.pos = 0

        def peek(self, kind=None, offset=0):
            token = self.tokens[self.pos + offset]
            return token[0] == kind if kind is not None else token

        def take(self, kind=None):
            token = self.tokens[self.pos]
            if kind is not None and token[0] != kind:
                raise ValueError("Unexpected token")
            self.pos += 1
            return token

        def parse(self):
            result = self.expression()
            self.take("EOF")
            return result

        def expression(self):
            node = self.term()
            while self.peek("+") or self.peek("-"):
                op = self.take()[0]
                node = ("bin", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.peek("*") or self.peek("/"):
                op = self.take()[0]
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.peek("-"):
                self.take("-")
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            if self.peek("NUM"):
                return ("num", self.take("NUM")[1])

            if self.peek("CELL"):
                return ("ref", self.take("CELL")[1])

            if self.peek("("):
                self.take("(")
                node = self.expression()
                self.take(")")
                return node

            name = self.take("NAME")[1]
            self.take("(")

            if name == "IF":
                left = self.expression()
                op = self.take()[0]
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Expected comparison operator")
                right = self.expression()
                self.take(",")
                then_expr = self.expression()
                self.take(",")
                else_expr = self.expression()
                self.take(")")
                return ("if", op, left, right, then_expr, else_expr)

            args = []
            while True:
                if self.peek("CELL") and self.peek(":", 1):
                    first = self.take("CELL")[1]
                    self.take(":")
                    second = self.take("CELL")[1]
                    args.append(("range", first, second))
                else:
                    args.append(("expr", self.expression()))

                if not self.peek(","):
                    break
                self.take(",")

            self.take(")")
            return ("func", name, args)

    ast_cache = {}
    values = {}
    state = {}

    def get_ast(name):
        if name not in ast_cache:
            content = cells[name].strip()
            ast_cache[name] = Parser(content[1:]).parse()
        return ast_cache[name]

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 2:
            return values[name]
        if state.get(name) == 1:
            return CYCLE

        state[name] = 1
        content = cells[name].strip()

        if not content.startswith("="):
            result = int(content)
        else:
            result = evaluate(get_ast(name))

        values[name] = result
        state[name] = 2
        return result

    def evaluate(node):
        kind = node[0]

        if kind == "num":
            return node[1]

        if kind == "ref":
            return evaluate_cell(node[1])

        if kind == "neg":
            value = evaluate(node[1])
            return value if value in ERRORS else -value

        if kind == "bin":
            left = evaluate(node[2])
            if left in ERRORS:
                return left

            right = evaluate(node[3])
            if right in ERRORS:
                return right

            op = node[1]
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return DIV_ZERO

            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient

        if kind == "if":
            left = evaluate(node[2])
            if left in ERRORS:
                return left

            right = evaluate(node[3])
            if right in ERRORS:
                return right

            op = node[1]
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(node[4] if condition else node[5])

        name, args = node[1], node[2]
        collected = []

        for arg in args:
            if arg[0] == "expr":
                value = evaluate(arg[1])
                if value in ERRORS:
                    return value
                collected.append(value)
                continue

            first, second = arg[1], arg[2]
            c1, r1 = ord(first[0]) - 65, int(first[1:])
            c2, r2 = ord(second[0]) - 65, int(second[1:])

            for row in range(min(r1, r2), max(r1, r2) + 1):
                for col in range(min(c1, c2), max(c1, c2) + 1):
                    cell_name = chr(65 + col) + str(row)
                    if cell_name not in cells:
                        continue
                    value = evaluate_cell(cell_name)
                    if value in ERRORS:
                        return value
                    collected.append(value)

        if name == "SUM":
            return sum(collected)
        if name == "MIN":
            return min(collected) if collected else 0
        return max(collected) if collected else 0

    return {name: evaluate_cell(name) for name in cells}
