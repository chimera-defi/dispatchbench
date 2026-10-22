def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import sys

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 10000))

    def cell_pos(name):
        return ord(name[0]) - ord('A'), int(name[1:])

    def tokenize(text):
        tokens = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch.isspace():
                i += 1
                continue
            if ch.isdigit():
                j = i + 1
                while j < len(text) and text[j].isdigit():
                    j += 1
                tokens.append(('INT', int(text[i:j])))
                i = j
                continue
            if ch.isalpha():
                j = i + 1
                while j < len(text) and text[j].isalnum():
                    j += 1
                word = text[i:j]
                tokens.append(('WORD', word))
                i = j
                continue
            if text.startswith('<>', i) or text.startswith('<=', i) or text.startswith('>=', i):
                tokens.append(('OP', text[i:i + 2]))
                i += 2
                continue
            if ch in '+-*/(),:=':
                tokens.append((ch, ch))
                i += 1
                continue
            if ch in '<>':
                tokens.append(('OP', ch))
                i += 1
                continue
            raise ValueError("Invalid formula")
        return tokens

    def parse_formula(text):
        tokens = tokenize(text)
        idx = 0

        def peek(kind=None):
            if idx >= len(tokens):
                return False if kind else None
            return tokens[idx][0] == kind if kind else tokens[idx]

        def take(kind=None):
            nonlocal idx
            if idx >= len(tokens) or (kind is not None and tokens[idx][0] != kind):
                raise ValueError("Invalid formula")
            token = tokens[idx]
            idx += 1
            return token

        def additive():
            node = term()
            while peek('+') or peek('-'):
                op = take()[0]
                node = ('bin', op, node, term())
            return node

        def term():
            node = unary()
            while peek('*') or peek('/'):
                op = take()[0]
                node = ('bin', op, node, unary())
            return node

        def unary():
            count = 0
            while peek('-'):
                take('-')
                count += 1
            node = atom()
            return ('neg', count, node) if count else node

        def atom():
            if peek('INT'):
                return ('int', take('INT')[1])
            if peek('WORD'):
                name = take('WORD')[1]
                if peek('('):
                    take('(')
                    if name == 'IF':
                        left = additive()
                        op = take('OP')[1] if peek('OP') else take('=')[1]
                        right = additive()
                        take(',')
                        then_expr = additive()
                        take(',')
                        else_expr = additive()
                        take(')')
                        return ('if', op, left, right, then_expr, else_expr)
                    args = []
                    if not peek(')'):
                        while True:
                            if peek('WORD') and idx + 1 < len(tokens) and tokens[idx + 1][0] == ':':
                                start = take('WORD')[1]
                                take(':')
                                end = take('WORD')[1]
                                c1, r1 = cell_pos(start)
                                c2, r2 = cell_pos(end)
                                args.append(('range', min(c1, c2), max(c1, c2),
                                             min(r1, r2), max(r1, r2)))
                            else:
                                args.append(additive())
                            if not peek(','):
                                break
                            take(',')
                    take(')')
                    return ('func', name, args)
                return ('ref', name)
            if peek('('):
                take('(')
                node = additive()
                take(')')
                return node
            raise ValueError("Invalid formula")

        result = additive()
        if idx != len(tokens):
            raise ValueError("Invalid formula")
        return result

    ast = {}
    for name, content in cells.items():
        stripped = content.strip()
        if stripped.startswith('='):
            ast[name] = parse_formula(stripped[1:])
        else:
            ast[name] = int(stripped)

    state = {}
    values = {}
    errors = {'#DIV/0!', '#CYCLE!'}

    def is_error(value):
        return isinstance(value, str) and value in errors

    def eval_cell(name):
        if name not in cells:
            return 0
        status = state.get(name, 0)
        if status == 2:
            return values[name]
        if status == 1:
            return '#CYCLE!'
        state[name] = 1
        value = ast[name] if isinstance(ast[name], int) else evaluate(ast[name])
        values[name] = value
        state[name] = 2
        return value

    def evaluate(node):
        kind = node[0]
        if kind == 'int':
            return node[1]
        if kind == 'ref':
            return eval_cell(node[1])
        if kind == 'neg':
            value = evaluate(node[2])
            if is_error(value):
                return value
            return -value if node[1] % 2 else value
        if kind == 'bin':
            left = evaluate(node[2])
            if is_error(left):
                return left
            right = evaluate(node[3])
            if is_error(right):
                return right
            op = node[1]
            if op == '+':
                return left + right
            if op == '-':
                return left - right
            if op == '*':
                return left * right
            if right == 0:
                return '#DIV/0!'
            quotient = abs(left) // abs(right)
            return -quotient if (left < 0) != (right < 0) else quotient
        if kind == 'if':
            left = evaluate(node[2])
            if is_error(left):
                return left
            right = evaluate(node[3])
            if is_error(right):
                return right
            op = node[1]
            condition = {
                '=': left == right,
                '<>': left != right,
                '<': left < right,
                '<=': left <= right,
                '>': left > right,
                '>=': left >= right,
            }[op]
            return evaluate(node[4] if condition else node[5])
        if kind == 'range':
            return node
        if kind == 'func':
            name, args = node[1], node[2]
            collected = []
            for arg in args:
                if arg[0] == 'range':
                    _, cmin, cmax, rmin, rmax = arg
                    for row in range(rmin, rmax + 1):
                        for col in range(cmin, cmax + 1):
                            cell_name = chr(ord('A') + col) + str(row)
                            if cell_name in cells:
                                value = eval_cell(cell_name)
                                if is_error(value):
                                    return value
                                collected.append(value)
                else:
                    value = evaluate(arg)
                    if is_error(value):
                        return value
                    collected.append(value)
            if name == 'SUM':
                return sum(collected)
            if not collected:
                return 0
            if name == 'MIN':
                return min(collected)
            return max(collected)
        raise ValueError("Invalid expression")

    return {name: eval_cell(name) for name in cells}
