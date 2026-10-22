import sys


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(10000)

    def tokenize(text):
        tokens = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch.isspace():
                i += 1
            elif ch.isdigit():
                j = i + 1
                while j < len(text) and text[j].isdigit():
                    j += 1
                tokens.append(("NUM", text[i:j]))
                i = j
            elif ch.isalpha():
                j = i + 1
                while j < len(text) and text[j].isalpha():
                    j += 1
                while j < len(text) and text[j].isdigit():
                    j += 1
                word = text[i:j]
                tokens.append(("CELL" if word[-1].isdigit() else "NAME", word))
                i = j
            elif text.startswith(("<=", ">=", "<>"), i):
                tokens.append(("OP", text[i:i + 2]))
                i += 2
            elif ch in "+-*/(),:":
                tokens.append((ch, ch))
                i += 1
            elif ch in "=<>":
                tokens.append(("OP", ch))
                i += 1
            else:
                raise ValueError("Invalid formula")
        tokens.append(("EOF", ""))
        return tokens

    class Parser:
        def __init__(self, text):
            self.tokens = tokenize(text)
            self.i = 0

        def peek(self, offset=0):
            return self.tokens[self.i + offset]

        def take(self, kind=None):
            token = self.peek()
            if kind is not None and token[0] != kind:
                raise ValueError("Invalid formula")
            self.i += 1
            return token

        def expression(self):
            node = self.term()
            while self.peek()[0] in ("+", "-"):
                op = self.take()[0]
                node = ("bin", op, node, self.term())
            return node

        def term(self):
            node = self.unary()
            while self.peek()[0] in ("*", "/"):
                op = self.take()[0]
                node = ("bin", op, node, self.unary())
            return node

        def unary(self):
            if self.peek()[0] == "-":
                self.take("-")
                return ("neg", self.unary())
            return self.atom()

        def atom(self):
            kind, value = self.peek()
            if kind == "NUM":
                self.take()
                return ("num", int(value))
            if kind == "CELL":
                self.take()
                return ("ref", value)
            if kind == "(":
                self.take("(")
                node = self.expression()
                self.take(")")
                return node
            if kind == "NAME":
                self.take()
                self.take("(")
                if value == "IF":
                    left = self.expression()
                    op = self.take("OP")[1]
                    right = self.expression()
                    self.take(",")
                    then_node = self.expression()
                    self.take(",")
                    else_node = self.expression()
                    self.take(")")
                    return ("if", op, left, right, then_node, else_node)

                args = []
                while True:
                    if (self.peek()[0] == "CELL"
                            and self.peek(1)[0] == ":"
                            and self.peek(2)[0] == "CELL"):
                        first = self.take("CELL")[1]
                        self.take(":")
                        second = self.take("CELL")[1]
                        args.append(("range", first, second))
                    else:
                        args.append(self.expression())
                    if self.peek()[0] != ",":
                        break
                    self.take(",")
                self.take(")")
                return ("func", value, args)
            raise ValueError("Invalid formula")

    parsed = {}
    for name, content in cells.items():
        if isinstance(content, int):
            parsed[name] = ("num", content)
        elif content.startswith("="):
            parser = Parser(content[1:])
            parsed[name] = parser.expression()
        else:
            parsed[name] = ("num", int(content))

    values = {}
    in_progress = set()
    ERROR_CYCLE = "#CYCLE!"
    ERROR_DIV = "#DIV/0!"

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in in_progress:
            return ERROR_CYCLE
        in_progress.add(name)
        result = evaluate(parsed[name])
        in_progress.remove(name)
        values[name] = result
        return result

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
                return ERROR_DIV
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
            checks = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(then_node if checks[op] else else_node)
        if kind == "func":
            _, function, args = node
            collected = []
            for arg in args:
                if arg[0] == "range":
                    _, first, second = arg
                    c1, r1 = ord(first[0]) - ord("A"), int(first[1:])
                    c2, r2 = ord(second[0]) - ord("A"), int(second[1:])
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(ord("A") + col) + str(row)
                            if name in cells:
                                value = cell_value(name)
                                if isinstance(value, str):
                                    return value
                                collected.append(value)
                else:
                    value = evaluate(arg)
                    if isinstance(value, str):
                        return value
                    collected.append(value)

            if function == "SUM":
                return sum(collected)
            if not collected:
                return 0
            return min(collected) if function == "MIN" else max(collected)

        raise ValueError("Invalid formula")

    return {name: cell_value(name) for name in cells}
