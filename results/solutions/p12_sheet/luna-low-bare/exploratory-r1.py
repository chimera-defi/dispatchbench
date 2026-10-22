def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    values = {}
    state = {}

    def cell_parts(name):
        return ord(name[0]) - ord("A"), int(name[1:]) - 1

    class Parser:
        def __init__(self, text):
            self.text = text
            self.i = 0

        def spaces(self):
            while self.i < len(self.text) and self.text[self.i].isspace():
                self.i += 1

        def peek(self):
            self.spaces()
            return self.text[self.i] if self.i < len(self.text) else ""

        def take(self, token):
            self.spaces()
            if self.text.startswith(token, self.i):
                self.i += len(token)
                return True
            return False

        def identifier(self):
            self.spaces()
            start = self.i
            while self.i < len(self.text) and self.text[self.i].isalpha():
                self.i += 1
            return self.text[start:self.i]

        def number(self):
            self.spaces()
            start = self.i
            while self.i < len(self.text) and self.text[self.i].isdigit():
                self.i += 1
            return int(self.text[start:self.i])

        def cell_name(self):
            self.spaces()
            start = self.i
            self.i += 1
            while self.i < len(self.text) and self.text[self.i].isdigit():
                self.i += 1
            return self.text[start:self.i]

        def formula(self):
            result = self.product()
            while True:
                op = self.peek()
                if op not in ("+", "-"):
                    return result
                self.i += 1
                result = (op, result, self.product())

        def product(self):
            result = self.unary()
            while True:
                op = self.peek()
                if op not in ("*", "/"):
                    return result
                self.i += 1
                result = (op, result, self.unary())

        def unary(self):
            if self.take("-"):
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            if self.take("("):
                node = self.formula()
                self.take(")")
                return node

            self.spaces()
            ch = self.text[self.i]
            if ch.isdigit():
                return ("num", self.number())

            name = self.identifier()
            if name in ("SUM", "MIN", "MAX"):
                self.take("(")
                args = []
                while True:
                    self.spaces()
                    save = self.i
                    first = self.cell_name()
                    self.spaces()
                    if self.take(":"):
                        second = self.cell_name()
                        args.append(("range", first, second))
                    else:
                        self.i = save
                        args.append(self.formula())
                    if not self.take(","):
                        break
                self.take(")")
                return ("func", name, args)

            if name == "IF":
                self.take("(")
                left = self.formula()
                self.spaces()
                op = None
                for candidate in ("<>", "<=", ">=", "=", "<", ">"):
                    if self.take(candidate):
                        op = candidate
                        break
                right = self.formula()
                self.take(",")
                yes = self.formula()
                self.take(",")
                no = self.formula()
                self.take(")")
                return ("if", op, left, right, yes, no)

            self.i = self.i - len(name)
            return ("ref", self.cell_name())

    def eval_cell(name):
        if name not in cells:
            return 0
        if state.get(name) == 1:
            return CYCLE
        if state.get(name) == 2:
            return values[name]

        state[name] = 1
        content = cells[name]
        if not content.startswith("="):
            try:
                result = int(content)
            except ValueError:
                result = 0
        else:
            tree = Parser(content[1:]).formula()
            result = evaluate(tree)
        values[name] = result
        state[name] = 2
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind in ("+", "-", "*", "/"):
            left = evaluate(node[1])
            if isinstance(left, str):
                return left
            right = evaluate(node[2])
            if isinstance(right, str):
                return right
            if kind == "+":
                return left + right
            if kind == "-":
                return left - right
            if kind == "*":
                return left * right
            if right == 0:
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, op, left_node, right_node, yes, no = node
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
            return evaluate(yes if condition else no)

        _, func, args = node
        collected = []
        for arg in args:
            if arg[0] == "range":
                _, a, b = arg
                col1, row1 = cell_parts(a)
                col2, row2 = cell_parts(b)
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        name = chr(ord("A") + col) + str(row + 1)
                        if name not in cells:
                            continue
                        value = eval_cell(name)
                        if isinstance(value, str):
                            return value
                        collected.append(value)
            else:
                value = evaluate(arg)
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

    for cell in cells:
        eval_cell(cell)
    return {cell: values[cell] for cell in cells}
