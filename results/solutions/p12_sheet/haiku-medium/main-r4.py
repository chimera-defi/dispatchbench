import sys

_DIV0 = "#DIV/0!"
_CYCLE = "#CYCLE!"


def _tokenize(text: str) -> list[tuple[str, object]]:
    toks = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif "0" <= c <= "9":
            j = i
            while j < n and "0" <= text[j] <= "9":
                j += 1
            toks.append(("INT", int(text[i:j])))
            i = j
        elif "A" <= c <= "Z":
            j = i + 1
            if j < n and "0" <= text[j] <= "9":
                while j < n and "0" <= text[j] <= "9":
                    j += 1
                toks.append(("CELL", text[i:j]))
            else:
                while j < n and "A" <= text[j] <= "Z":
                    j += 1
                toks.append(("WORD", text[i:j]))
            i = j
        else:
            two = text[i:i + 2]
            if two in ("<>", "<=", ">="):
                toks.append(("OP", two))
                i += 2
            else:
                toks.append(("OP", c))
                i += 1
    return toks


def _parse(text: str):
    toks = _tokenize(text)
    pos = 0

    def peek(k=0):
        return toks[pos + k] if pos + k < len(toks) else (None, None)

    def take():
        nonlocal pos
        tok = toks[pos]
        pos += 1
        return tok

    def is_op(vals):
        t = peek()
        return t[0] == "OP" and t[1] in vals

    def expr():
        node = term()
        while is_op(("+", "-")):
            op = take()[1]
            node = ("bin", op, node, term())
        return node

    def term():
        node = unary()
        while is_op(("*", "/")):
            op = take()[1]
            node = ("bin", op, node, unary())
        return node

    def unary():
        if is_op(("-",)):
            take()
            return ("neg", unary())
        return atom()

    def arg():
        t0, t1, t2 = peek(0), peek(1), peek(2)
        if t0[0] == "CELL" and t1 == ("OP", ":") and t2[0] == "CELL":
            take()
            take()
            take()
            return ("range", t0[1], t2[1])
        return expr()

    def atom():
        kind, val = take()
        if kind == "INT":
            return ("num", val)
        if kind == "CELL":
            return ("ref", val)
        if kind == "OP" and val == "(":
            node = expr()
            take()  # ')'
            return node
        if kind == "WORD":
            take()  # '('
            if val == "IF":
                left = expr()
                op = take()[1]
                right = expr()
                take()  # ','
                then = expr()
                take()  # ','
                other = expr()
                take()  # ')'
                return ("if", op, left, right, then, other)
            args = [arg()]
            while is_op((",",)):
                take()
                args.append(arg())
            take()  # ')'
            return ("func", val, args)
        raise ValueError("bad formula token")

    return expr()


def _range_names(a: str, b: str):
    c1, c2 = sorted((a[0], b[0]))
    r1, r2 = sorted((int(a[1:]), int(b[1:])))
    for r in range(r1, r2 + 1):
        for c in range(ord(c1), ord(c2) + 1):
            yield chr(c) + str(r)


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

    values: dict[str, int | str] = {}
    active: set[str] = set()

    def cell_value(name: str):
        if name in values:
            return values[name]
        if name not in cells:
            return 0
        if name in active:
            return _CYCLE
        active.add(name)
        raw = cells[name].strip()
        if raw.startswith("="):
            v = ev(_parse(raw[1:]))
        else:
            v = int(raw)
        active.discard(name)
        values[name] = v
        return v

    def ev(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            v = ev(node[1])
            return v if isinstance(v, str) else -v
        if kind == "bin":
            op = node[1]
            left = ev(node[2])
            if isinstance(left, str):
                return left
            right = ev(node[3])
            if isinstance(right, str):
                return right
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return _DIV0
            q = abs(left) // abs(right)
            return q if (left < 0) == (right < 0) else -q
        if kind == "if":
            _, op, l, r, t, e = node
            a = ev(l)
            if isinstance(a, str):
                return a
            b = ev(r)
            if isinstance(b, str):
                return b
            if op == "=":
                ok = a == b
            elif op == "<>":
                ok = a != b
            elif op == "<":
                ok = a < b
            elif op == "<=":
                ok = a <= b
            elif op == ">":
                ok = a > b
            else:
                ok = a >= b
            return ev(t) if ok else ev(e)
        if kind == "func":
            fname, args = node[1], node[2]
            vals = []
            for a in args:
                if a[0] == "range":
                    for name in _range_names(a[1], a[2]):
                        if name in cells:
                            v = cell_value(name)
                            if isinstance(v, str):
                                return v
                            vals.append(v)
                else:
                    v = ev(a)
                    if isinstance(v, str):
                        return v
                    vals.append(v)
            if not vals:
                return 0
            if fname == "SUM":
                return sum(vals)
            if fname == "MIN":
                return min(vals)
            return max(vals)
        raise ValueError("unknown node")

    return {name: cell_value(name) for name in cells}
