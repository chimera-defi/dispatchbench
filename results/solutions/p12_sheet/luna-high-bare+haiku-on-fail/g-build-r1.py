import re
import sys

def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(100000)

    tokens_re = re.compile(
        r"\s*(<=|>=|<>|[()+\-*/,:=<>]|[A-Z][0-9]+|\d+|[A-Z]+)"
    )

    def tokenize(text):
        tokens = []
        pos = 0
        while pos < len(text):
            match = tokens_re.match(text, pos)
            if not match:
                raise ValueError("Invalid formula")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    def parse_formula(text):
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

        def expression():
            node = product()
            while peek() in ("+", "-"):
                op = take()
                node = ("bin", op, node, product())
            return node

        def product():
            node = unary()
            while peek() in ("*", "/"):
                op = take()
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() == "-":
                take("-")
                return ("neg", unary())
            return atom()

        def atom():
            token = peek()
            if token == "(":
                take("(")
                node = expression()
                take(")")
                return node
            if token is None:
                raise ValueError("Invalid formula")
            if token.isdigit():
                take()
                return ("num", int(token))
            if token in ("SUM", "MIN", "MAX", "IF"):
                name = take()
                take("(")
                if name == "IF":
                    left = expression()
                    op = take()
                    if op not in ("=", "<>", "<", "<=", ">", ">="):
                        raise ValueError("Invalid formula")
                    right = expression()
                    take(",")
                    then_node = expression()
                    take(",")
                    else_node = expression()
                    take(")")
                    return ("if", left, op, right, then_node, else_node)

                args = []
                while True:
                    if (
                        peek() is not None
                        and re.fullmatch(r"[A-Z][0-9]+", peek())
                        and pos + 1 < len(tokens)
                        and tokens[pos + 1] == ":"
                    ):
                        start = take()
                        take(":")
                        end = take()
                        args.append(("range", start, end))
                    else:
                        args.append(("formula", expression()))
                    if peek() != ",":
                        break
                    take(",")
                take(")")
                return ("func", name, args)
            if re.fullmatch(r"[A-Z][0-9]+", token):
                take()
                return ("ref", token)
            raise ValueError("Invalid formula")

        result = expression()
        if pos != len(tokens):
            raise ValueError("Invalid formula")
        return result

    parsed = {}
    for name, content in cells.items():
        if content.startswith("="):
            parsed[name] = parse_formula(content[1:])
        else:
            parsed[name] = int(content)

    values = {}
    active = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return "#CYCLE!"
        active.add(name)
        content = parsed[name]
        value = content if isinstance(content, int) else evaluate(content)
        active.remove(name)
        values[name] = value
        return value

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
                return "#DIV/0!"
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, left_node, op, right_node, then_node, else_node = node
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
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
            return evaluate(then_node if conditions[op] else else_node)

        _, name, args = node
        collected = []
        for arg in args:
            if arg[0] == "formula":
                value = evaluate(arg[1])
                if isinstance(value, str):
                    return value
                collected.append(value)
            else:
                _, start, end = arg
                col1, row1 = ord(start[0]) - ord("A"), int(start[1:])
                col2, row2 = ord(end[0]) - ord("A"), int(end[1:])
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        cell = chr(ord("A") + col) + str(row)
                        if cell in cells:
                            value = cell_value(cell)
                            if isinstance(value, str):
                                return value
                            collected.append(value)

        if name == "SUM":
            return sum(collected)
        if not collected:
            return 0
        return min(collected) if name == "MIN" else max(collected)

    for name in cells:
        cell_value(name)
    return values
