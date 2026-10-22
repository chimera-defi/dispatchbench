def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    import re
    import sys
    import threading

    ERR_DIV = "#DIV/0!"
    ERR_CYCLE = "#CYCLE!"
    FUNCS = ("SUM", "MIN", "MAX", "IF")
    TOKEN_RE = re.compile(r"\s*(<>|<=|>=|[-+*/(),:=<>]|[0-9]+|[A-Za-z][A-Za-z0-9]*)")
    CELL_RE = re.compile(r"[A-Z][1-9][0-9]?")

    def tokenize(text):
        tokens = []
        pos = 0
        while text[pos:].strip():
            match = TOKEN_RE.match(text, pos)
            if match is None:
                raise ValueError(f"Invalid formula: {text!r}")
            tokens.append(match.group(1))
            pos = match.end()
        return tokens

    def parse(tokens):
        state = [0]

        def peek(offset=0):
            i = state[0] + offset
            return tokens[i] if i < len(tokens) else None

        def take():
            tok = peek()
            state[0] += 1
            return tok

        def expect(tok):
            if take() != tok:
                raise ValueError(f"Expected {tok!r}")

        def expr():
            node = term()
            while peek() in ("+", "-"):
                op = take()
                node = ("bin", op, node, term())
            return node

        def term():
            node = unary()
            while peek() in ("*", "/"):
                op = take()
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() == "-":
                take()
                return ("neg", unary())
            return atom()

        def atom():
            tok = take()
            if tok == "(":
                node = expr()
                expect(")")
                return node
            if tok.isdigit():
                return ("num", int(tok))
            if CELL_RE.fullmatch(tok):
                return ("ref", tok)
            if tok in FUNCS:
                expect("(")
                if tok == "IF":
                    return if_call()
                args = [arg()]
                while peek() == ",":
                    take()
                    args.append(arg())
                expect(")")
                return ("func", tok, args)
            raise ValueError(f"Unexpected token {tok!r}")

        def arg():
            if CELL_RE.fullmatch(peek() or "") and peek(1) == ":":
                start = take()
                take()
                end = take()
                return ("range", start, end)
            return expr()

        def if_call():
            left = expr()
            op = take()
            right = expr()
            expect(",")
            then = expr()
            expect(",")
            other = expr()
            expect(")")
            return ("if", op, left, right, then, other)

        node = expr()
        if state[0] != len(tokens):
            raise ValueError("Trailing tokens in formula")
        return node

    parsed = {
        name: parse(tokenize(content[1:]))
        for name, content in cells.items()
        if content.startswith("=")
    }

    cache = {}
    in_progress = set()

    def div(a, b):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    def compare(left, op, right):
        if op == "=":
            return left == right
        if op == "<>":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        return left >= right

    def combine(fn, current, value):
        if current is None:
            return value
        if fn == "SUM":
            return current + value
        if fn == "MIN":
            return min(current, value)
        return max(current, value)

    def range_cells(start, end):
        c1, r1 = ord(start[0]) - 65, int(start[1:])
        c2, r2 = ord(end[0]) - 65, int(end[1:])
        for row in range(min(r1, r2), max(r1, r2) + 1):
            for col in range(min(c1, c2), max(c1, c2) + 1):
                yield chr(65 + col) + str(row)

    def aggregate(fn, args):
        result = None
        for arg in args:
            if arg[0] == "range":
                for name in range_cells(arg[1], arg[2]):
                    if name not in cells:
                        continue
                    value = get(name)
                    if isinstance(value, str):
                        return value
                    result = combine(fn, result, value)
            else:
                value = ev(arg)
                if isinstance(value, str):
                    return value
                result = combine(fn, result, value)
        return 0 if result is None else result

    def ev(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return get(node[1])
        if kind == "neg":
            value = ev(node[1])
            return value if isinstance(value, str) else -value
        if kind == "bin":
            left = ev(node[2])
            if isinstance(left, str):
                return left
            right = ev(node[3])
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
                return ERR_DIV
            return div(left, right)
        if kind == "if":
            _, op, left_node, right_node, then_node, other_node = node
            left = ev(left_node)
            if isinstance(left, str):
                return left
            right = ev(right_node)
            if isinstance(right, str):
                return right
            return ev(then_node if compare(left, op, right) else other_node)
        if kind == "func":
            return aggregate(node[1], node[2])
        raise ValueError(f"Unknown node {kind!r}")

    def get(name):
        if name not in cells:
            return 0
        if name in cache:
            return cache[name]
        if name in in_progress:
            return ERR_CYCLE
        in_progress.add(name)
        content = cells[name]
        if content.startswith("="):
            value = ev(parsed[name])
        else:
            value = int(content.strip())
        in_progress.discard(name)
        cache[name] = value
        return value

    result = {}
    failure = []

    def run():
        try:
            for name in cells:
                result[name] = get(name)
        except BaseException as exc:
            failure.append(exc)

    old_limit = sys.getrecursionlimit()
    old_stack = threading.stack_size()
    sys.setrecursionlimit(max(old_limit, 1_000_000))
    threading.stack_size(256 * 1024 * 1024)
    try:
        worker = threading.Thread(target=run)
        worker.start()
        worker.join()
    finally:
        sys.setrecursionlimit(old_limit)
        threading.stack_size(old_stack)

    if failure:
        raise failure[0]
    return result
