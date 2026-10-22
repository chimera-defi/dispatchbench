def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    class ParseError(Exception):
        pass

    def cell_order(name):
        return (int(name[1:]), ord(name[0]) - ord("A"))

    def tokenize(source):
        tokens = []
        i = 0
        while i < len(source):
            ch = source[i]
            if ch.isspace():
                i += 1
            elif ch.isdigit():
                j = i + 1
                while j < len(source) and source[j].isdigit():
                    j += 1
                tokens.append(("INT", int(source[i:j])))
                i = j
            elif ch.isalpha():
                j = i + 1
                while j < len(source) and source[j].isalpha():
                    j += 1
                word = source[i:j]
                if len(word) == 1 and j < len(source) and source[j].isdigit():
                    k = j + 1
                    while k < len(source) and source[k].isdigit():
                        k += 1
                    tokens.append(("CELL", word + source[j:k]))
                    i = k
                else:
                    tokens.append(("IDENT", word))
                    i = j
            elif source.startswith("<>", i) or source.startswith("<=", i) or source.startswith(">=", i):
                tokens.append(("OP", source[i:i + 2]))
                i += 2
            elif ch in "+-*/(),:=":
                tokens.append((ch, ch))
                i += 1
            elif ch in "<>":
                tokens.append(("OP", ch))
                i += 1
            else:
                raise ParseError
        tokens.append(("EOF", None))
        return tokens

    class Parser:
        def __init__(self, source):
            self.tokens = tokenize(source)
            self.i = 0

        def peek(self, kind=None):
            token = self.tokens[self.i]
            return token[0] == kind if kind is not None else token

        def take(self, kind=None):
            token = self.tokens[self.i]
            if kind is not None and token[0] != kind:
                raise ParseError
            self.i += 1
            return token

        def formula(self):
            return self.expression()

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
            if self.peek("INT"):
                return ("int", self.take("INT")[1])
            if self.peek("CELL"):
                return ("ref", self.take("CELL")[1])
            if self.peek("("):
                self.take("(")
                node = self.formula()
                self.take(")")
                return node
            if self.peek("IDENT"):
                name = self.take("IDENT")[1].upper()
                self.take("(")
                if name in ("SUM", "MIN", "MAX"):
                    args = []
                    while True:
                        if self.peek("CELL") and self.tokens[self.i + 1][0] == ":":
                            start = self.take("CELL")[1]
                            self.take(":")
                            end = self.take("CELL")[1]
                            args.append(("range", start, end))
                        else:
                            args.append(self.formula())
                        if not self.peek(","):
                            break
                        self.take(",")
                    self.take(")")
                    return ("func", name, args)
                if name == "IF":
                    left = self.formula()
                    op = self.take("OP")[1] if self.peek("OP") else self.take("=")[1]
                    right = self.formula()
                    self.take(",")
                    yes = self.formula()
                    self.take(",")
                    no = self.formula()
                    self.take(")")
                    return ("if", left, op, right, yes, no)
                raise ParseError
            raise ParseError

    asts = {}
    for name, content in cells.items():
        stripped = content.strip()
        if stripped.startswith("="):
            parser = Parser(stripped[1:])
            ast = parser.formula()
            parser.take("EOF")
            asts[name] = ast
        else:
            asts[name] = ("int", int(stripped))

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    memo = {}
    active = set()

    def is_error(value):
        return isinstance(value, str)

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return -q if (a < 0) != (b < 0) else q

    def eval_cell(name):
        if name not in cells:
            return 0
        if name in memo:
            return memo[name]
        if name in active:
            return CYCLE
        active.add(name)
        value = evaluate(asts[name])
        active.remove(name)
        memo[name] = value
        return value

    def evaluate(node):
        kind = node[0]
        if kind == "int":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if is_error(value) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
            if is_error(right):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return DIV0
            return trunc_div(left, right)
        if kind == "if":
            _, left_node, op, right_node, yes_node, no_node = node
            left = evaluate(left_node)
            if is_error(left):
                return left
            right = evaluate(right_node)
            if is_error(right):
                return right
            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(yes_node if comparisons[op] else no_node)

        _, function, args = node
        values = []
        for arg in args:
            if arg[0] == "range":
                start, end = arg[1], arg[2]
                r1, c1 = cell_order(start)
                r2, c2 = cell_order(end)
                for row in range(min(r1, r2), max(r1, r2) + 1):
                    for col in range(min(c1, c2), max(c1, c2) + 1):
                        cell = chr(ord("A") + col) + str(row)
                        if cell in cells:
                            value = eval_cell(cell)
                            if is_error(value):
                                return value
                            values.append(value)
            else:
                value = evaluate(arg)
                if is_error(value):
                    return value
                values.append(value)

        if function == "SUM":
            return sum(values)
        if function == "MIN":
            return min(values) if values else 0
        return max(values) if values else 0

    result = {}
    for name in sorted(cells, key=cell_order):
        value = eval_cell(name)
        result[name] = value
    return result
