import operator
import sys
import threading


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    ERR_DIV = "#DIV/0!"
    ERR_CYCLE = "#CYCLE!"
    COMPARE = {
        "=": operator.eq,
        "<>": operator.ne,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
    }

    def tokenize(s):
        toks = []
        i, n = 0, len(s)
        while i < n:
            c = s[i]
            if c.isspace():
                i += 1
            elif c.isdigit():
                j = i
                while j < n and s[j].isdigit():
                    j += 1
                toks.append(("INT", int(s[i:j])))
                i = j
            elif "A" <= c <= "Z":
                j = i
                while j < n and "A" <= s[j] <= "Z":
                    j += 1
                if j - i == 1 and j < n and s[j].isdigit():
                    k = j
                    while k < n and s[k].isdigit():
                        k += 1
                    toks.append(("CELL", s[i:k]))
                    i = k
                else:
                    toks.append(("FUNC", s[i:j]))
                    i = j
            elif s[i:i + 2] in ("<>", "<=", ">="):
                toks.append(("OP", s[i:i + 2]))
                i += 2
            elif c in "+-*/(),:=<>":
                toks.append(("OP", c))
                i += 1
            else:
                raise ValueError(f"bad character {c!r}")
        return toks

    def span(a, b):
        ca, ra = a[0], int(a[1:])
        cb, rb = b[0], int(b[1:])
        cols = range(min(ord(ca), ord(cb)), max(ord(ca), ord(cb)) + 1)
        rows = range(min(ra, rb), max(ra, rb) + 1)
        # Row-major: top row first, left to right within a row.
        return [chr(c) + str(r) for r in rows for c in cols]

    def parse(toks):
        pos = 0

        def peek(off=0):
            return toks[pos + off] if pos + off < len(toks) else ("END", None)

        def advance():
            nonlocal pos
            t = peek()
            pos += 1
            return t

        def expect_op(v):
            if advance() != ("OP", v):
                raise ValueError(f"expected {v!r}")

        def formula():
            node = term()
            while peek() in (("OP", "+"), ("OP", "-")):
                op = advance()[1]
                node = ("bin", op, node, term())
            return node

        def term():
            node = unary()
            while peek() in (("OP", "*"), ("OP", "/")):
                op = advance()[1]
                node = ("bin", op, node, unary())
            return node

        def unary():
            if peek() == ("OP", "-"):
                advance()
                return ("neg", unary())
            return atom()

        def arg():
            if peek()[0] == "CELL" and peek(1) == ("OP", ":") and peek(2)[0] == "CELL":
                a = advance()[1]
                advance()
                b = advance()[1]
                return ("range", span(a, b))
            return formula()

        def if_call():
            left = formula()
            op = advance()
            if op[0] != "OP" or op[1] not in COMPARE:
                raise ValueError("expected comparison operator")
            right = formula()
            expect_op(",")
            then_node = formula()
            expect_op(",")
            else_node = formula()
            expect_op(")")
            return ("if", op[1], left, right, then_node, else_node)

        def atom():
            kind, val = advance()
            if kind == "INT":
                return ("num", val)
            if kind == "CELL":
                return ("ref", val)
            if (kind, val) == ("OP", "("):
                node = formula()
                expect_op(")")
                return node
            if kind == "FUNC":
                expect_op("(")
                if val == "IF":
                    return if_call()
                args = [arg()]
                while peek() == ("OP", ","):
                    advance()
                    args.append(arg())
                expect_op(")")
                return ("func", val, args)
            raise ValueError("unexpected token")

        node = formula()
        if pos != len(toks):
            raise ValueError("trailing tokens")
        return node

    memo = {}
    busy = set()

    def get_cell(name):
        if name not in cells:
            return 0
        if name in memo:
            return memo[name]
        if name in busy:
            return ERR_CYCLE
        busy.add(name)
        content = cells[name].strip()
        if content.startswith("="):
            value = evaluate(parse(tokenize(content[1:])))
        else:
            value = int(content)
        busy.discard(name)
        memo[name] = value
        return value

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return get_cell(node[1])
        if kind == "neg":
            v = evaluate(node[1])
            return v if isinstance(v, str) else -v
        if kind == "bin":
            op = node[1]
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
            if isinstance(right, str):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return ERR_DIV
            q = abs(left) // abs(right)
            return q if (left < 0) == (right < 0) else -q
        if kind == "func":
            name, args = node[1], node[2]
            values = []
            for a in args:
                if a[0] == "range":
                    for nm in a[1]:
                        if nm in cells:
                            v = get_cell(nm)
                            if isinstance(v, str):
                                return v
                            values.append(v)
                else:
                    v = evaluate(a)
                    if isinstance(v, str):
                        return v
                    values.append(v)
            if name == "SUM":
                return sum(values)
            if not values:
                return 0
            return min(values) if name == "MIN" else max(values)
        # kind == "if"
        _, op, l_node, r_node, t_node, e_node = node
        left = evaluate(l_node)
        if isinstance(left, str):
            return left
        right = evaluate(r_node)
        if isinstance(right, str):
            return right
        return evaluate(t_node if COMPARE[op](left, right) else e_node)

    def solve():
        return {name: get_cell(name) for name in cells}

    # Formula chains can be up to 2574 cells deep, so run on a thread with a large stack.
    box = {}

    def runner():
        box["result"] = solve()

    old_stack = threading.stack_size(256 * 1024 * 1024)
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))
    t = threading.Thread(target=runner)
    t.start()
    t.join()
    threading.stack_size(old_stack)
    return box["result"]
