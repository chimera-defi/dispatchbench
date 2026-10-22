def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    ERROR_DIV = "#DIV/0!"
    ERROR_CYCLE = "#CYCLE!"
    cache = {}
    visiting = set()

    token_re = re.compile(
        r"\s*(?:(\d+)|([A-Z](?:[1-9]\d?))|(<=|>=|<>|[+\-*/(),:=<>]))"
    )

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            number, name, symbol = match.groups()
            tokens.append(number if number is not None else name if name is not None else symbol)
            pos = match.end()
        tokens.append(None)
        return tokens

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if name in cache:
            return cache[name]
        if name in visiting:
            return ERROR_CYCLE

        visiting.add(name)
        content = cells[name]
        if content.startswith("="):
            parser = Parser(tokenize(content[1:]))
            value = parser.parse_formula()
        else:
            value = int(content)
        visiting.remove(name)
        cache[name] = value
        return value

    def cell_parts(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.index = 0

        def peek(self):
            return self.tokens[self.index]

        def take(self):
            token = self.peek()
            self.index += 1
            return token

        def parse_formula(self):
            return self.parse_add()

        def parse_add(self):
            value = self.parse_mul()
            while self.peek() in ("+", "-"):
                op = self.take()
                if isinstance(value, str):
                    self.parse_mul()
                    return value
                right = self.parse_mul()
                if isinstance(right, str):
                    return right
                value = value + right if op == "+" else value - right
            return value

        def parse_mul(self):
            value = self.parse_unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                if isinstance(value, str):
                    self.parse_unary()
                    return value
                right = self.parse_unary()
                if isinstance(right, str):
                    return right
                if op == "*":
                    value *= right
                elif right == 0:
                    return ERROR_DIV
                else:
                    quotient = abs(value) // abs(right)
                    value = -quotient if (value < 0) != (right < 0) else quotient
            return value

        def parse_unary(self):
            if self.peek() == "-":
                self.take()
                value = self.parse_unary()
                return value if isinstance(value, str) else -value
            return self.parse_atom()

        def parse_atom(self):
            token = self.take()
            if token == "(":
                value = self.parse_formula()
                self.take()  # )
                return value
            if token is None:
                raise ValueError("Unexpected end of formula")
            if token.isdigit():
                return int(token)
            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.parse_function(token)
            return evaluate_cell(token)

        def parse_function(self, function):
            self.take()  # (
            if function == "IF":
                left = self.parse_formula()
                op = self.take()
                right = self.parse_formula()
                self.take()  # comma
                if isinstance(left, str):
                    self.parse_formula()
                    self.take()  # comma
                    self.parse_formula()
                    self.take()  # )
                    return left
                if isinstance(right, str):
                    self.parse_formula()
                    self.take()  # comma
                    self.parse_formula()
                    self.take()  # )
                    return right
                then_value = self.parse_formula()
                self.take()  # comma
                else_value = self.parse_formula()
                self.take()  # )
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
                return then_value if condition else else_value

            values = []
            while True:
                # A range is two adjacent cell-name tokens separated by ':'.
                if (
                    self.peek() is not None
                    and re.fullmatch(r"[A-Z][1-9]\d?", self.peek())
                    and self.tokens[self.index + 1] == ":"
                ):
                    start = self.take()
                    self.take()
                    end = self.take()
                    c1, r1 = cell_parts(start)
                    c2, r2 = cell_parts(end)
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(ord("A") + col) + str(row)
                            if name in cells:
                                value = evaluate_cell(name)
                                if isinstance(value, str):
                                    self.skip_remaining_arguments()
                                    return value
                                values.append(value)
                else:
                    value = self.parse_formula()
                    if isinstance(value, str):
                        self.skip_remaining_arguments()
                        return value
                    values.append(value)

                if self.peek() != ",":
                    break
                self.take()
            self.take()  # )
            if function == "SUM":
                return sum(values)
            if not values:
                return 0
            if function == "MIN":
                return min(values)
            return max(values)

        def skip_remaining_arguments(self):
            # Consume syntactically without evaluating formulas or references.
            depth = 0
            while self.peek() is not None:
                token = self.take()
                if token == "(":
                    depth += 1
                elif token == ")":
                    if depth == 0:
                        return
                    depth -= 1

    result = {}
    for name in cells:
        result[name] = evaluate_cell(name)
    return result
