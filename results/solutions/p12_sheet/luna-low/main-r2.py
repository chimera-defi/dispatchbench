def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    token_re = re.compile(
        r"\s*(?:(\d+)|([A-Z][1-9]\d?)|(<>|<=|>=|[+\-*/(),:=<>]))"
    )

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            number, cell, operator = match.groups()
            tokens.append(number or cell or operator)
            pos = match.end()
        return tokens

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = tokenize(content[1:])
        else:
            parsed[name] = int(content)

    values = {}
    state = {}  # 1 means currently evaluating; values are cached on completion.

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if state.get(name) == 1:
            return CYCLE

        state[name] = 1
        item = parsed[name]
        result = item if isinstance(item, int) else Parser(item).parse()
        values[name] = result
        state[name] = 2
        return result

    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.pos += 1
            return token

        def parse(self):
            result = self.expression()
            if self.peek() is not None:
                raise ValueError("Unexpected token")
            return result

        def expression(self):
            value = self.term()
            while self.peek() in ("+", "-"):
                op = self.take()
                if isinstance(value, str):
                    return value
                right = self.term()
                if isinstance(right, str):
                    return right
                value = value + right if op == "+" else value - right
            return value

        def term(self):
            value = self.unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                if isinstance(value, str):
                    return value
                right = self.unary()
                if isinstance(right, str):
                    return right
                if op == "*":
                    value *= right
                elif right == 0:
                    value = DIV0
                else:
                    quotient = abs(value) // abs(right)
                    value = -quotient if (value < 0) != (right < 0) else quotient
            return value

        def unary(self):
            if self.peek() == "-":
                self.take()
                value = self.unary()
                return value if isinstance(value, str) else -value
            return self.atom()

        def atom(self):
            token = self.take()
            if token is None:
                raise ValueError("Unexpected end")
            if token == "(":
                value = self.expression()
                self.take()  # ")"
                return value
            if token.isdigit():
                return int(token)
            if token in ("SUM", "MIN", "MAX", "IF"):
                return self.function(token)
            return evaluate_cell(token)

        def function(self, name):
            self.take()  # "("
            if name == "IF":
                left = self.expression()
                op = self.take()
                right = self.expression()
                self.take()  # ","
                then_value = self.expression()
                self.take()  # ","
                else_value = self.expression()
                self.take()  # ")"

                if isinstance(left, str):
                    return left
                if isinstance(right, str):
                    return right
                conditions = {
                    "=": left == right,
                    "<>": left != right,
                    "<": left < right,
                    "<=": left <= right,
                    ">": left > right,
                    ">=": left >= right,
                }
                return then_value if conditions[op] else else_value

            aggregate = 0 if name == "SUM" else None
            while True:
                # A range begins with a cell token followed by ":".
                if (
                    self.peek() is not None
                    and re.fullmatch(r"[A-Z][1-9]\d?", self.peek())
                    and self.pos + 1 < len(self.tokens)
                    and self.tokens[self.pos + 1] == ":"
                ):
                    first = self.take()
                    self.take()
                    second = self.take()
                    cells_in_range = range_cells(first, second)
                    for cell_name in cells_in_range:
                        if cell_name not in cells:
                            continue
                        value = evaluate_cell(cell_name)
                        if isinstance(value, str):
                            return value
                        if name == "SUM":
                            aggregate += value
                        elif aggregate is None:
                            aggregate = value
                        elif name == "MIN":
                            aggregate = min(aggregate, value)
                        else:
                            aggregate = max(aggregate, value)
                else:
                    value = self.expression()
                    if isinstance(value, str):
                        return value
                    if name == "SUM":
                        aggregate += value
                    elif aggregate is None:
                        aggregate = value
                    elif name == "MIN":
                        aggregate = min(aggregate, value)
                    else:
                        aggregate = max(aggregate, value)

                if self.peek() != ",":
                    break
                self.take()
            self.take()  # ")"
            return 0 if aggregate is None else aggregate

    def range_cells(first, second):
        col1, row1 = ord(first[0]) - ord("A"), int(first[1:])
        col2, row2 = ord(second[0]) - ord("A"), int(second[1:])
        min_col, max_col = sorted((col1, col2))
        min_row, max_row = sorted((row1, row2))
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                yield chr(ord("A") + col) + str(row)

    return {name: evaluate_cell(name) for name in cells}
