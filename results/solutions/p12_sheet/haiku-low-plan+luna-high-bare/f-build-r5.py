import re
import sys


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(100000)

    error_div = "#DIV/0!"
    error_cycle = "#CYCLE!"
    error_values = {error_div, error_cycle}

    def is_error(value):
        return isinstance(value, str) and value in error_values

    def tokenize(formula):
        pattern = re.compile(r"\s+|[0-9]+|[A-Z]+[0-9]*|<>|<=|>=|[+\-*/(),:=<>]")
        tokens = []
        pos = 0
        while pos < len(formula):
            match = pattern.match(formula, pos)
            if not match:
                raise ValueError("Invalid formula")
            token = match.group()
            pos = match.end()
            if not token.isspace():
                tokens.append(token)
        return tokens

    def parse_formula(formula):
        tokens = tokenize(formula)
        index = 0

        def peek():
            return tokens[index] if index < len(tokens) else None

        def take():
            nonlocal index
            token = peek()
            index += 1
            return token

        def parse_expr():
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
            if peek() == "-":
                take()
                return ("neg", parse_unary())
            return parse_atom()

        def parse_atom():
            token = peek()
            if token == "(":
                take()
                node = parse_expr()
                take()  # )
                return node
            if token is not None and token.isdigit():
                take()
                return ("num", int(token))
            if token in ("SUM", "MIN", "MAX"):
                name = take()
                take()  # (
                args = []
                while True:
                    if (
                        peek() is not None
                        and re.fullmatch(r"[A-Z][0-9]+", peek())
                        and index + 1 < len(tokens)
                        and tokens[index + 1] == ":"
                    ):
                        first = take()
                        take()  # :
                        second = take()
                        args.append(("range", first, second))
                    else:
                        args.append(parse_expr())
                    if peek() != ",":
                        break
                    take()
                take()  # )
                return ("func", name, args)
            if token == "IF":
                take()
                take()  # (
                left = parse_expr()
                op = take()
                right = parse_expr()
                take()  # ,
                then_node = parse_expr()
                take()  # ,
                else_node = parse_expr()
                take()  # )
                return ("if", op, left, right, then_node, else_node)
            if token is not None and re.fullmatch(r"[A-Z][0-9]+", token):
                take()
                return ("ref", token)
            raise ValueError("Invalid formula")

        result = parse_expr()
        return result

    asts = {}
    for name, content in cells.items():
        if content.startswith("="):
            asts[name] = parse_formula(content[1:])

    state = {}
    values = {}

    def cell_value(name):
        if name not in cells:
            return 0
        if state.get(name) == 2:
            return values[name]
        if state.get(name) == 1:
            return error_cycle

        state[name] = 1
        content = cells[name]
        if not content.startswith("="):
            result = int(content.strip())
        else:
            result = eval_node(asts[name])
        values[name] = result
        state[name] = 2
        return result

    def eval_node(node):
        kind = node[0]

        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            value = eval_node(node[1])
            return value if is_error(value) else -value
        if kind == "bin":
            _, op, left_node, right_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left
            right = eval_node(right_node)
            if is_error(right):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return error_div
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            _, op, left_node, right_node, then_node, else_node = node
            left = eval_node(left_node)
            if is_error(left):
                return left
            right = eval_node(right_node)
            if is_error(right):
                return right
            conditions = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return eval_node(then_node if conditions[op] else else_node)
        if kind == "func":
            _, name, args = node
            found = False
            aggregate = None

            for arg in args:
                if arg[0] == "range":
                    _, first, second = arg
                    col1, row1 = ord(first[0]) - ord("A"), int(first[1:])
                    col2, row2 = ord(second[0]) - ord("A"), int(second[1:])
                    for row in range(min(row1, row2), max(row1, row2) + 1):
                        for col in range(min(col1, col2), max(col1, col2) + 1):
                            cell = chr(ord("A") + col) + str(row)
                            if cell not in cells:
                                continue
                            value = cell_value(cell)
                            if is_error(value):
                                return value
                            if not found:
                                aggregate = value
                                found = True
                            elif name == "SUM":
                                aggregate += value
                            elif name == "MIN":
                                aggregate = min(aggregate, value)
                            else:
                                aggregate = max(aggregate, value)
                else:
                    value = eval_node(arg)
                    if is_error(value):
                        return value
                    if not found:
                        aggregate = value
                        found = True
                    elif name == "SUM":
                        aggregate += value
                    elif name == "MIN":
                        aggregate = min(aggregate, value)
                    else:
                        aggregate = max(aggregate, value)

            return aggregate if found else 0

        raise ValueError("Invalid AST")

    return {name: cell_value(name) for name in cells}
