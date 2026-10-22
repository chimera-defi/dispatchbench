def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys

    sys.setrecursionlimit(20000)

    DIV_ZERO = "#DIV/0!"
    CYCLE = "#CYCLE!"

    def tokenize(formula):
        s = re.sub(r"\s+", "", formula)
        tokens = []
        i = 0
        while i < len(s):
            c = s[i]
            if c.isdigit():
                j = i + 1
                while j < len(s) and s[j].isdigit():
                    j += 1
                tokens.append(("INT", s[i:j]))
                i = j
            elif c.isalpha():
                j = i + 1
                while j < len(s) and s[j].isalpha():
                    j += 1
                while j < len(s) and s[j].isdigit():
                    j += 1
                word = s[i:j]
                if word in ("SUM", "MIN", "MAX", "IF"):
                    tokens.append(("FUNC", word))
                else:
                    tokens.append(("CELL", word))
                i = j
            elif s.startswith("<>", i) or s.startswith("<=", i) or s.startswith(">=", i):
                tokens.append(("OP", s[i:i + 2]))
                i += 2
            else:
                tokens.append((c, c))
                i += 1
        return tokens

    def parse(formula):
        tokens = tokenize(formula)
        pos = 0

        def peek():
            return tokens[pos][0] if pos < len(tokens) else None

        def take(expected=None):
            nonlocal pos
            if pos >= len(tokens):
                raise ValueError("Invalid formula")
            token = tokens[pos]
            if expected is not None and token[0] != expected:
                raise ValueError("Invalid formula")
            pos += 1
            return token

        def additive():
            node = multiplicative()
            while peek() in ("+", "-"):
                op = take()[0]
                node = ("bin", op, node, multiplicative())
            return node

        def multiplicative():
            node = unary()
            while peek() in ("*", "/"):
                op = take()[0]
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() == "-":
                take("-")
                return ("neg", unary())
            return atom()

        def arguments():
            result = []
            while True:
                if peek() == "CELL" and pos + 1 < len(tokens) and tokens[pos + 1][0] == ":":
                    start = take("CELL")[1]
                    take(":")
                    end = take("CELL")[1]
                    result.append(("range", start, end))
                else:
                    result.append(("expr", additive()))
                if peek() != ",":
                    break
                take(",")
            return result

        def atom():
            kind = peek()
            if kind == "INT":
                return ("int", int(take("INT")[1]))
            if kind == "CELL":
                return ("cell", take("CELL")[1])
            if kind == "(":
                take("(")
                node = additive()
                take(")")
                return node
            if kind == "FUNC":
                func = take("FUNC")[1]
                take("(")
                if func == "IF":
                    left = additive()
                    op = take("OP" if peek() == "OP" else "=")[1]
                    right = additive()
                    take(",")
                    then_expr = additive()
                    take(",")
                    else_expr = additive()
                    take(")")
                    return ("if", left, op, right, then_expr, else_expr)
                args = arguments()
                take(")")
                return ("func", func, args)
            raise ValueError("Invalid formula")

        result = additive()
        if pos != len(tokens):
            raise ValueError("Invalid formula")
        return result

    state = {}
    values = {}
    trees = {}

    def cell_coords(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def get(name):
        if name not in cells:
            return 0
        status = state.get(name)
        if status == 2:
            return values[name]
        if status == 1:
            return CYCLE

        content = cells[name]
        if not content.startswith("="):
            result = int(content)
            values[name] = result
            state[name] = 2
            return result

        state[name] = 1
        if name not in trees:
            trees[name] = parse(content[1:])
        result = evaluate(trees[name])
        values[name] = result
        state[name] = 2
        return result

    def evaluate(node):
        kind = node[0]
        if kind == "int":
            return node[1]
        if kind == "cell":
            return get(node[1])
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
                return DIV_ZERO
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
            comparisons = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return evaluate(then_node if comparisons[op] else else_node)

        _, func, args = node
        result_values = []
        for arg in args:
            if arg[0] == "expr":
                value = evaluate(arg[1])
                if isinstance(value, str):
                    return value
                result_values.append(value)
            else:
                _, start, end = arg
                col1, row1 = cell_coords(start)
                col2, row2 = cell_coords(end)
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        name = chr(ord("A") + col) + str(row)
                        if name in cells:
                            value = get(name)
                            if isinstance(value, str):
                                return value
                            result_values.append(value)

        if not result_values:
            return 0
        if func == "SUM":
            return sum(result_values)
        if func == "MIN":
            return min(result_values)
        return max(result_values)

    return {name: get(name) for name in cells}
