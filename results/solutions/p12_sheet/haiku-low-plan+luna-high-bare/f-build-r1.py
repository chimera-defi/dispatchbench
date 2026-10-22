def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    def tokenize(source):
        tokens = []
        i = 0
        while i < len(source):
            ch = source[i]
            if ch.isspace():
                i += 1
            elif ch.isdigit():
                j = i + 1
                while j < len(source) and source[j].isdigit():
                    j += 1
                tokens.append(("int", int(source[i:j])))
                i = j
            elif ch.isalpha():
                j = i + 1
                while j < len(source) and source[j].isalpha():
                    j += 1
                word = source[i:j]
                if len(word) == 1 and j < len(source) and source[j].isdigit():
                    k = j + 1
                    while k < len(source) and source[k].isdigit():
                        k += 1
                    tokens.append(("cell", word + source[j:k]))
                    i = k
                else:
                    tokens.append(("name", word))
                    i = j
            elif source.startswith("<>", i) or source.startswith("<=", i) or source.startswith(">=", i):
                tokens.append(("op", source[i:i + 2]))
                i += 2
            else:
                tokens.append(("op", ch))
                i += 1
        return tokens

    def parse(source):
        tokens = tokenize(source)
        pos = 0

        def peek():
            return tokens[pos] if pos < len(tokens) else None

        def take():
            nonlocal pos
            token = tokens[pos]
            pos += 1
            return token

        def expression():
            node = term()
            while peek() and peek()[1] in ("+", "-"):
                op = take()[1]
                node = ("bin", op, node, term())
            return node

        def term():
            node = unary()
            while peek() and peek()[1] in ("*", "/"):
                op = take()[1]
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() and peek()[1] == "-":
                take()
                return ("neg", unary())
            return atom()

        def atom():
            token = take()
            if token[0] == "int":
                return ("num", token[1])
            if token[0] == "cell":
                return ("ref", token[1])
            if token[1] == "(":
                node = expression()
                take()  # )
                return node
            if token[0] == "name":
                function = token[1]
                take()  # (
                if function == "IF":
                    left = expression()
                    comparison = take()[1]
                    right = expression()
                    take()  # ,
                    then_node = expression()
                    take()  # ,
                    else_node = expression()
                    take()  # )
                    return ("if", comparison, left, right, then_node, else_node)

                args = []
                while True:
                    if peek() and peek()[0] == "cell" and pos + 1 < len(tokens) and tokens[pos + 1][1] == ":":
                        first = take()[1]
                        take()  # :
                        second = take()[1]
                        args.append(("range", first, second))
                    else:
                        args.append(("formula", expression()))
                    if peek() and peek()[1] == ",":
                        take()
                    else:
                        take()  # )
                        break
                return ("func", function, args)
            raise ValueError("Invalid formula")

        return expression()

    asts = {}
    for name, content in cells.items():
        content = content.strip()
        asts[name] = parse(content[1:]) if content.startswith("=") else ("num", int(content))

    memo = {}
    in_progress = set()

    def coordinates(name):
        return ord(name[0]) - ord("A"), int(name[1:])

    def eval_cell(name):
        if name not in cells:
            return 0
        if name in memo:
            return memo[name]
        if name in in_progress:
            return CYCLE
        in_progress.add(name)
        value = evaluate(asts[name])
        in_progress.remove(name)
        memo[name] = value
        return value

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return eval_cell(node[1])
        if kind == "neg":
            value = evaluate(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            op, left_node, right_node = node[1], node[2], node[3]
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
                return DIV0
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == "if":
            comparison, left_node, right_node, then_node, else_node = node[1:]
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            tests = {
                "=": lambda: left == right,
                "<>": lambda: left != right,
                "<": lambda: left < right,
                "<=": lambda: left <= right,
                ">": lambda: left > right,
                ">=": lambda: left >= right,
            }
            return evaluate(then_node if tests[comparison]() else else_node)

        _, function, args = node
        values = []
        for arg in args:
            if arg[0] == "formula":
                value = evaluate(arg[1])
                if isinstance(value, str):
                    return value
                values.append(value)
            else:
                _, first, second = arg
                col1, row1 = coordinates(first)
                col2, row2 = coordinates(second)
                for row in range(min(row1, row2), max(row1, row2) + 1):
                    for col in range(min(col1, col2), max(col1, col2) + 1):
                        name = chr(ord("A") + col) + str(row)
                        if name in cells:
                            value = eval_cell(name)
                            if isinstance(value, str):
                                return value
                            values.append(value)

        if function == "SUM":
            return sum(values)
        if not values:
            return 0
        return min(values) if function == "MIN" else max(values)

    def sort_key(name):
        col, row = coordinates(name)
        return row, col

    return {name: eval_cell(name) for name in sorted(cells, key=sort_key)}
