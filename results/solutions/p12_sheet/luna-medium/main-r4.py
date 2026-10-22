def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re

    error_values = {"#DIV/0!", "#CYCLE!"}
    cache = {}
    visiting = set()
    cell_pattern = re.compile(r"[A-Z](?:[1-9][0-9]?)")
    token_pattern = re.compile(
        r"\s*(<=|>=|<>|[()+\-*/,:=<>]|[A-Z]+|[0-9]+)"
    )

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = token_pattern.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    def cell_name(token):
        return bool(cell_pattern.fullmatch(token))

    def evaluate_cell(name):
        if name not in cells:
            return 0
        if name in cache:
            return cache[name]
        if name in visiting:
            return "#CYCLE!"

        visiting.add(name)
        content = cells[name]
        if content.startswith("="):
            value = evaluate_formula(content[1:])
        else:
            value = int(content)
        visiting.remove(name)
        cache[name] = value
        return value

    def evaluate_formula(text):
        tokens = tokenize(text)
        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else None

        def take(expected=None):
            nonlocal pos
            token = peek()
            if token is None or (expected is not None and token != expected):
                raise ValueError("Invalid formula")
            pos += 1
            return token

        def parse_expression():
            value = parse_product()
            while peek() in ("+", "-"):
                op = take()
                if value in error_values:
                    return value
                right = parse_product()
                if right in error_values:
                    value = right
                else:
                    value = value + right if op == "+" else value - right
            return value

        def parse_product():
            value = parse_unary()
            while peek() in ("*", "/"):
                op = take()
                if value in error_values:
                    return value
                right = parse_unary()
                if right in error_values:
                    value = right
                elif op == "*":
                    value *= right
                elif right == 0:
                    value = "#DIV/0!"
                else:
                    quotient = abs(value) // abs(right)
                    value = -quotient if (value < 0) != (right < 0) else quotient
            return value

        def parse_unary():
            if peek() == "-":
                take("-")
                value = parse_unary()
                return value if value in error_values else -value
            return parse_atom()

        def parse_atom():
            token = peek()
            if token == "(":
                take("(")
                value = parse_expression()
                take(")")
                return value
            if token is not None and token.isdigit():
                return int(take())
            if token is None:
                raise ValueError("Invalid formula")
            if token in ("SUM", "MIN", "MAX", "IF"):
                return parse_function()
            if cell_name(token):
                return evaluate_cell(take())
            raise ValueError("Invalid formula")

        def parse_function():
            function = take()
            take("(")
            if function == "IF":
                left = parse_expression()
                op = take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid formula")
                right = parse_expression()
                take(",")
                if left in error_values:
                    return left
                if right in error_values:
                    return right
                condition = {
                    "=": left == right,
                    "<>": left != right,
                    "<": left < right,
                    "<=": left <= right,
                    ">": left > right,
                    ">=": left >= right,
                }[op]
                if condition:
                    chosen = parse_expression()
                    take(",")
                    skip_expression()
                    take(")")
                    return chosen
                skip_expression()
                take(",")
                chosen = parse_expression()
                take(")")
                return chosen

            aggregate = []
            while True:
                first = parse_expression()
                if cell_name(first) and peek() == ":":
                    take(":")
                    second = take()
                    if not cell_name(second):
                        raise ValueError("Invalid formula")
                    col1, row1 = ord(first[0]) - 65, int(first[1:])
                    col2, row2 = ord(second[0]) - 65, int(second[1:])
                    for row in range(min(row1, row2), max(row1, row2) + 1):
                        for col in range(min(col1, col2), max(col1, col2) + 1):
                            name = chr(col + 65) + str(row)
                            if name in cells:
                                value = evaluate_cell(name)
                                if value in error_values:
                                    return value
                                aggregate.append(value)
                else:
                    if first in error_values:
                        return first
                    aggregate.append(first)

                if peek() != ",":
                    break
                take(",")
            take(")")
            if function == "SUM":
                return sum(aggregate)
            if not aggregate:
                return 0
            return min(aggregate) if function == "MIN" else max(aggregate)

        def skip_expression():
            # Parse the unevaluated IF branch while ignoring its value.
            nonlocal pos
            depth = 0
            while pos < len(tokens):
                token = tokens[pos]
                if token in ("(",):
                    depth += 1
                elif token == ")":
                    if depth == 0:
                        return
                    depth -= 1
                elif token == "," and depth == 0:
                    return
                pos += 1

        result = parse_expression()
        if pos != len(tokens):
            raise ValueError("Invalid formula")
        return result

    return {name: evaluate_cell(name) for name in cells}
