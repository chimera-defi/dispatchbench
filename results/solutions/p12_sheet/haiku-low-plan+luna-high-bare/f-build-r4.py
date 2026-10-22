import re
import sys


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    def tokenize(source):
        tokens = []
        i = 0
        while i < len(source):
            if source[i].isspace():
                i += 1
                continue

            if source.startswith("<>", i) or source.startswith("<=", i) or source.startswith(">=", i):
                tokens.append(source[i:i + 2])
                i += 2
                continue

            ch = source[i]
            if ch in "+-*/(),: =<>":
                tokens.append(ch)
                i += 1
                continue

            if ch.isalnum():
                j = i + 1
                while j < len(source) and source[j].isalnum():
                    j += 1
                word = source[i:j]
                if word.isdigit():
                    tokens.append(("INT", int(word)))
                else:
                    tokens.append(("WORD", word))
                i = j
                continue

            raise ValueError("Invalid formula")

        return tokens

    def is_cell(token):
        return (
            isinstance(token, tuple)
            and token[0] == "WORD"
            and re.fullmatch(r"[A-Z](?:[1-9]|[1-9][0-9])", token[1]) is not None
        )

    def parse_formula(source):
        tokens = tokenize(source)
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

        def parse_additive():
            node = parse_term()
            while peek() in ("+", "-"):
                op = take()
                node = ("bin", op, node, parse_term())
            return node

        def parse_term():
            node = parse_unary()
            while peek() in ("*", "/"):
                op = take()
                node = ("bin", op, node, parse_unary())
            return node

        def parse_unary():
            count = 0
            while peek() == "-":
                take("-")
                count += 1
            node = parse_atom()
            return ("neg", count, node) if count else node

        def parse_function(name):
            take("(")
            if name == "IF":
                left = parse_additive()
                op = take()
                if op not in ("=", "<>", "<", "<=", ">", ">="):
                    raise ValueError("Invalid comparison")
                right = parse_additive()
                take(",")
                then_node = parse_additive()
                take(",")
                else_node = parse_additive()
                take(")")
                return ("if", left, op, right, then_node, else_node)

            args = []
            while True:
                if is_cell(peek()) and pos + 1 < len(tokens) and tokens[pos + 1] == ":":
                    first = take()[1]
                    take(":")
                    second_token = take()
                    if not is_cell(second_token):
                        raise ValueError("Invalid range")
                    second = second_token[1]
                    c1, r1 = ord(first[0]) - 65, int(first[1:])
                    c2, r2 = ord(second[0]) - 65, int(second[1:])
                    args.append(("range", min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2)))
                else:
                    args.append(parse_additive())

                if peek() != ",":
                    break
                take(",")
            take(")")
            return ("func", name, args)

        def parse_atom():
            token = peek()
            if isinstance(token, tuple) and token[0] == "INT":
                take()
                return ("num", token[1])

            if is_cell(token):
                take()
                return ("ref", token[1])

            if token == "(":
                take("(")
                node = parse_additive()
                take(")")
                return node

            if isinstance(token, tuple) and token[0] == "WORD":
                name = token[1]
                if name not in ("SUM", "MIN", "MAX", "IF"):
                    raise ValueError("Invalid function")
                take()
                return parse_function(name)

            raise ValueError("Invalid formula")

        result = parse_additive()
        if pos != len(tokens):
            raise ValueError("Invalid formula")
        return result

    ast = {}
    for name, content in cells.items():
        text = content.strip()
        if text.startswith("="):
            ast[name] = parse_formula(text[1:])
        else:
            ast[name] = int(text)

    state = {}
    values = {}

    def eval_cell(name):
        if name not in cells:
            return 0
        status = state.get(name, 0)
        if status == 2:
            return values[name]
        if status == 1:
            return "#CYCLE!"

        state[name] = 1
        tree = ast[name]
        result = tree if isinstance(tree, int) else evaluate(tree)
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
            value = evaluate(node[2])
            if isinstance(value, str):
                return value
            return -value if node[1] % 2 else value
        if kind == "bin":
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
            if isinstance(right, str):
                return right

            op = node[1]
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
            left = evaluate(node[1])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
            if isinstance(right, str):
                return right

            op = node[2]
            condition = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return evaluate(node[4] if condition else node[5])

        if kind == "range":
            _, min_col, min_row, max_col, max_row = node
            result = []
            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    name = chr(65 + col) + str(row)
                    if name in cells:
                        value = eval_cell(name)
                        if isinstance(value, str):
                            return value
                        result.append(value)
            return result

        if kind == "func":
            name, args = node[1], node[2]
            values_list = []
            for arg in args:
                value = evaluate(arg)
                if isinstance(value, str):
                    return value
                if isinstance(value, list):
                    values_list.extend(value)
                else:
                    values_list.append(value)

            if not values_list:
                return 0
            if name == "SUM":
                return sum(values_list)
            if name == "MIN":
                return min(values_list)
            return max(values_list)

        raise ValueError("Invalid expression")

    return {name: eval_cell(name) for name in cells}
