def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    errors = {"#DIV/0!", "#CYCLE!"}
    values = {}
    state = {}

    def cell_index(name):
        return (int(name[1:]) - 1) * 26 + ord(name[0]) - ord("A")

    def cell_name(index):
        return chr(ord("A") + index % 26) + str(index // 26 + 1)

    def get_cell(name):
        if name not in cells:
            return 0
        s = state.get(name, 0)
        if s == 1:
            return "#CYCLE!"
        if s == 2:
            return values[name]

        state[name] = 1
        content = cells[name].strip()
        if content.startswith("="):
            parser = Parser(content[1:])
            value = parser.parse_expression()
        else:
            value = int(content)
        state[name] = 2
        values[name] = value
        return value

    class Parser:
        token_re = re.compile(r"\s*(<=|>=|<>|[A-Za-z][0-9]+|-?\d+|[()+*/,:=<>-])")

        def __init__(self, text):
            self.tokens = []
            pos = 0
            while pos < len(text):
                match = self.token_re.match(text, pos)
                if not match:
                    raise ValueError("Invalid formula")
                self.tokens.append(match.group(1))
                pos = match.end()
            self.i = 0

        def peek(self):
            return self.tokens[self.i] if self.i < len(self.tokens) else None

        def take(self):
            token = self.peek()
            self.i += 1
            return token

        def expect(self, token):
            if self.take() != token:
                raise ValueError("Invalid formula")

        def parse_expression(self):
            return self.parse_add()

        def parse_add(self):
            value = self.parse_mul()
            while self.peek() in ("+", "-"):
                op = self.take()
                if value in errors:
                    return value
                right = self.parse_mul()
                if right in errors:
                    return right
                value = value + right if op == "+" else value - right
            return value

        def parse_mul(self):
            value = self.parse_unary()
            while self.peek() in ("*", "/"):
                op = self.take()
                if value in errors:
                    return value
                right = self.parse_unary()
                if right in errors:
                    return right
                if op == "*":
                    value *= right
                elif right == 0:
                    return "#DIV/0!"
                else:
                    quotient = abs(value) // abs(right)
                    value = -quotient if (value < 0) != (right < 0) else quotient
            return value

        def parse_unary(self):
            if self.peek() == "-":
                self.take()
                value = self.parse_unary()
                return value if value in errors else -value
            return self.parse_atom()

        def parse_atom(self):
            token = self.take()
            if token == "(":
                value = self.parse_expression()
                self.expect(")")
                return value
            if token is None:
                raise ValueError("Unexpected end")
            if token.isdigit():
                return int(token)
            if token in ("SUM", "MIN", "MAX"):
                return self.parse_aggregate(token)
            if token == "IF":
                return self.parse_if()
            return get_cell(token)

        def parse_aggregate(self, function):
            self.expect("(")
            results = []
            while True:
                start = self.peek()
                if (start is not None and re.fullmatch(r"[A-Z][1-9][0-9]?", start)
                        and self.i + 1 < len(self.tokens)
                        and self.tokens[self.i + 1] == ":"):
                    first = self.take()
                    self.take()
                    second = self.take()
                    c1, r1 = ord(first[0]) - 65, int(first[1:])
                    c2, r2 = ord(second[0]) - 65, int(second[1:])
                    for row in range(min(r1, r2), max(r1, r2) + 1):
                        for col in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(65 + col) + str(row)
                            if name in cells:
                                value = get_cell(name)
                                if value in errors:
                                    return value
                                results.append(value)
                else:
                    value = self.parse_expression()
                    if value in errors:
                        return value
                    results.append(value)

                if self.peek() != ",":
                    break
                self.take()
            self.expect(")")
            if not results:
                return 0
            if function == "SUM":
                return sum(results)
            if function == "MIN":
                return min(results)
            return max(results)

        def parse_if(self):
            self.expect("(")
            left = self.parse_expression()
            if left in errors:
                return left
            op = self.take()
            right = self.parse_expression()
            if right in errors:
                return right
            self.expect(",")
            then_value = None
            else_text_start = self.i

            # Parse branches lazily by identifying their token boundaries.
            then_start = self.i
            then_end = self.find_argument_end(then_start)
            self.i = then_end
            self.expect(",")
            else_start = self.i
            else_end = self.find_argument_end(else_start)
            self.i = else_end
            self.expect(")")

            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            self.i = then_start if comparisons[op] else else_start
            value = self.parse_expression()
            if self.i != (then_end if comparisons[op] else else_end):
                raise ValueError("Invalid branch")
            self.i = else_end
            self.expect(")")
            return value

        def find_argument_end(self, start):
            depth = 0
            j = start
            while j < len(self.tokens):
                token = self.tokens[j]
                if token == "(":
                    depth += 1
                elif token == ")":
                    if depth == 0:
                        return j
                    depth -= 1
                elif token == "," and depth == 0:
                    return j
                j += 1
            return j

    # Evaluate all present cells; recursion depth may reach the number of cells.
    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    for name in cells:
        get_cell(name)
    return {name: values[name] for name in cells}
