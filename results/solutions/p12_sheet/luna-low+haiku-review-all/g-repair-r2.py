def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    ERROR_DIV = "#DIV/0!"
    ERROR_CYCLE = "#CYCLE!"
    CELL_RE = re.compile(r"[A-Z][1-9]\d?")
    TOKEN_RE = re.compile(r"\d+|[A-Z][1-9]\d?|[A-Z]+|<=|>=|<>|[-+*/(),:=<>]")
    FUNCTIONS = ("SUM", "MIN", "MAX", "IF")
    COMPARE = {
        "=": lambda a, b: a == b,
        "<>": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }
    cache = {}
    visiting = set()

    # Deep reference chains recurse through several frames per cell.
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    def is_error(value):
        return isinstance(value, str)

    def tokenize(text):
        tokens = []
        pos = 0
        while True:
            while pos < len(text) and text[pos].isspace():
                pos += 1
            if pos == len(text):
                break
            match = TOKEN_RE.match(text, pos)
            if match is None:
                raise ValueError("Invalid formula")
            tokens.append(match.group(0))
            pos = match.end()
        tokens.append(None)
        return tokens

    def range_names(start, end):
        c1, r1 = ord(start[0]) - ord("A"), int(start[1:])
        c2, r2 = ord(end[0]) - ord("A"), int(end[1:])
        for row in range(min(r1, r2), max(r1, r2) + 1):
            for col in range(min(c1, c2), max(c1, c2) + 1):
                yield chr(ord("A") + col) + str(row)

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
            value = Parser(tokenize(content[1:])).parse_formula()
        else:
            value = int(content)
        visiting.discard(name)
        cache[name] = value
        return value

    class Parser:
        # When live is False, nothing is evaluated: cells are not read and
        # no cache entries are made. Only the tokens are consumed.
        def __init__(self, tokens, live=True):
            self.tokens = tokens
            self.index = 0
            self.live = live

        def peek(self):
            return self.tokens[self.index]

        def take(self):
            token = self.tokens[self.index]
            self.index += 1
            return token

        def parse_with(self, parse, live):
            saved = self.live
            self.live = saved and live
            try:
                return parse()
            finally:
                self.live = saved

        def parse_formula(self):
            value = self.parse_term()
            while self.peek() in ("+", "-"):
                op = self.take()
                right = self.parse_with(self.parse_term, not is_error(value))
                if is_error(value):
                    continue
                if is_error(right):
                    value = right
                elif op == "+":
                    value += right
                else:
                    value -= right
            return value

        def parse_term(self):
            value = self.parse_unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                right = self.parse_with(self.parse_unary, not is_error(value))
                if is_error(value):
                    continue
                if is_error(right):
                    value = right
                elif op == "*":
                    value *= right
                elif right == 0:
                    value = ERROR_DIV
                else:
                    # Truncate toward zero.
                    quotient = abs(value) // abs(right)
                    value = quotient if (value < 0) == (right < 0) else -quotient
            return value

        def parse_unary(self):
            if self.peek() == "-":
                self.take()
                value = self.parse_unary()
                return value if is_error(value) else -value
            return self.parse_atom()

        def parse_atom(self):
            token = self.take()
            if token == "(":
                value = self.parse_formula()
                self.take()  # )
                return value
            if token.isdigit():
                return int(token)
            if token in FUNCTIONS:
                return self.parse_call(token)
            if not self.live:
                return 0
            return evaluate_cell(token)

        def parse_call(self, function):
            self.take()  # (
            if function == "IF":
                return self.parse_if()

            values = []
            failed = None
            while True:
                if CELL_RE.fullmatch(self.peek()) and self.tokens[self.index + 1] == ":":
                    start = self.take()
                    self.take()  # :
                    end = self.take()
                    if failed is None and self.live:
                        for name in range_names(start, end):
                            if name in cells:
                                value = evaluate_cell(name)
                                if is_error(value):
                                    failed = value
                                    break
                                values.append(value)
                else:
                    value = self.parse_with(self.parse_formula, failed is None)
                    if failed is None:
                        if is_error(value):
                            failed = value
                        else:
                            values.append(value)

                if self.peek() != ",":
                    break
                self.take()  # ,
            self.take()  # )

            if failed is not None:
                return failed
            if function == "SUM":
                return sum(values)
            if not values:
                return 0
            return min(values) if function == "MIN" else max(values)

        def parse_if(self):
            # Both comparison operands are always evaluated, left then right.
            left = self.parse_formula()
            op = self.take()
            right = self.parse_formula()
            self.take()  # ,

            failed = left if is_error(left) else right if is_error(right) else None
            cond = failed is None and COMPARE[op](left, right)

            then_value = self.parse_with(self.parse_formula, cond)
            self.take()  # ,
            else_value = self.parse_with(self.parse_formula, failed is None and not cond)
            self.take()  # )

            if failed is not None:
                return failed
            return then_value if cond else else_value

    return {name: evaluate_cell(name) for name in cells}
