import sys


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(100000)

    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"
    COMPARE = {
        "=": lambda a, b: a == b,
        "<>": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }

    def tokenize(s):
        toks = []
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch.isspace():
                i += 1
            elif ch.isdigit():
                j = i
                while j < n and s[j].isdigit():
                    j += 1
                toks.append(("num", int(s[i:j])))
                i = j
            elif ch.isalpha():
                j = i
                while j < n and s[j].isalpha():
                    j += 1
                word = s[i:j]
                k = j
                while k < n and s[k].isdigit():
                    k += 1
                if len(word) == 1 and k > j:
                    toks.append(("cell", word + s[j:k]))
                    i = k
                else:
                    toks.append(("func", word))
                    i = j
            elif s[i:i + 2] in ("<>", "<=", ">="):
                toks.append(("op", s[i:i + 2]))
                i += 2
            elif ch in "+-*/():,=<>":
                toks.append(("op", ch))
                i += 1
            else:
                raise ValueError(f"bad character {ch!r}")
        return toks

    def parse_formula(text):
        toks = tokenize(text)
        pos = [0]

        def peek():
            return toks[pos[0]] if pos[0] < len(toks) else (None, None)

        def take():
            t = peek()
            pos[0] += 1
            return t

        def expect(op):
            if take() != ("op", op):
                raise ValueError(f"expected {op!r}")

        def parse_expr():
            node = parse_term()
            while peek() in (("op", "+"), ("op", "-")):
                op = take()[1]
                node = ("bin", op, node, parse_term())
            return node

        def parse_term():
            node = parse_unary()
            while peek() in (("op", "*"), ("op", "/")):
                op = take()[1]
                node = ("bin", op, node, parse_unary())
            return node

        def parse_unary():
            if peek() == ("op", "-"):
                take()
                return ("neg", parse_unary())
            return parse_atom()

        def parse_atom():
            t = take()
            if t[0] == "num":
                return ("num", t[1])
            if t[0] == "cell":
                return ("ref", t[1])
            if t == ("op", "("):
                e = parse_expr()
                expect(")")
                return e
            if t[0] == "func":
                name = t[1].upper()
                expect("(")
                if name == "IF":
                    left = parse_expr()
                    op = take()
                    if op[0] != "op" or op[1] not in COMPARE:
                        raise ValueError("expected comparison")
                    right = parse_expr()
                    expect(",")
                    then = parse_expr()
                    expect(",")
                    other = parse_expr()
                    expect(")")
                    return ("if", left, op[1], right, then, other)
                args = []
                while True:
                    p = pos[0]
                    if (p + 2 < len(toks) and toks[p][0] == "cell"
                            and toks[p + 1] == ("op", ":")
                            and toks[p + 2][0] == "cell"):
                        args.append(("range", toks[p][1], toks[p + 2][1]))
                        pos[0] += 3
                    else:
                        args.append(parse_expr())
                    if peek() == ("op", ","):
                        take()
                        continue
                    break
                expect(")")
                return ("call", name, args)
            raise ValueError("unexpected token")

        return parse_expr()

    def range_names(c1, c2):
        col1, row1 = ord(c1[0]) - 65, int(c1[1:])
        col2, row2 = ord(c2[0]) - 65, int(c2[1:])
        cols = range(min(col1, col2), max(col1, col2) + 1)
        rows = range(min(row1, row2), max(row1, row2) + 1)
        for r in rows:
            for c in cols:
                yield chr(65 + c) + str(r)

    parsed = {}
    for name, content in cells.items():
        s = content.strip()
        if s.startswith("="):
            parsed[name] = parse_formula(s[1:])
        else:
            parsed[name] = ("num", int(s))

    value = {}
    busy = set()

    def get(name):
        if name not in parsed:
            return 0
        if name in value:
            return value[name]
        if name in busy:
            return CYCLE
        busy.add(name)
        v = ev(parsed[name])
        busy.discard(name)
        value[name] = v
        return v

    def call(fname, args):
        vals = []
        for a in args:
            if a[0] == "range":
                for name in range_names(a[1], a[2]):
                    if name in parsed:
                        v = get(name)
                        if isinstance(v, str):
                            return v
                        vals.append(v)
            else:
                v = ev(a)
                if isinstance(v, str):
                    return v
                vals.append(v)
        if fname == "SUM":
            return sum(vals)
        if not vals:
            return 0
        return min(vals) if fname == "MIN" else max(vals)

    def ev(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return get(node[1])
        if kind == "neg":
            v = ev(node[1])
            return v if isinstance(v, str) else -v
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
                return DIV0
            q = abs(left) // abs(right)
            return q if (left < 0) == (right < 0) else -q
        if kind == "if":
            left = ev(node[1])
            if isinstance(left, str):
                return left
            right = ev(node[3])
            if isinstance(right, str):
                return right
            branch = node[4] if COMPARE[node[2]](left, right) else node[5]
            return ev(branch)
        if kind == "call":
            return call(node[1], node[2])
        raise ValueError("unknown node")

    return {name: get(name) for name in cells}
