import operator
import re
import sys

_DIV0 = "#DIV/0!"
_CYCLE = "#CYCLE!"

_TOKEN = re.compile(r"\s*(?:(\d+)|([A-Z]+\d*)|(<>|<=|>=|[-+*/(),:=<>]))")
_CMP = {
    "=": operator.eq,
    "<>": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


def _tokenize(text):
    toks = []
    text = text.rstrip()
    pos = 0
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise ValueError("bad formula: %r" % text)
        pos = m.end()
        if m.group(1) is not None:
            toks.append(("num", m.group(1)))
        elif m.group(2) is not None:
            w = m.group(2)
            toks.append(("cell" if re.fullmatch(r"[A-Z]\d+", w) else "id", w))
        else:
            toks.append(("op", m.group(3)))
    return toks


def _col_row(name):
    return ord(name[0]) - 65, int(name[1:])


def _parse(text):
    toks = _tokenize(text)
    pos = 0

    def peek(k=0):
        i = pos + k
        return toks[i] if i < len(toks) else (None, None)

    def take():
        nonlocal pos
        t = toks[pos]
        pos += 1
        return t

    def formula():
        node = term()
        while peek() in (("op", "+"), ("op", "-")):
            op = take()[1]
            node = ("bin", op, node, term())
        return node

    def term():
        node = unary()
        while peek() in (("op", "*"), ("op", "/")):
            op = take()[1]
            node = ("bin", op, node, unary())
        return node

    def unary():
        if peek() == ("op", "-"):
            take()
            return ("neg", unary())
        return atom()

    def arg():
        if peek(0)[0] == "cell" and peek(1) == ("op", ":") and peek(2)[0] == "cell":
            a = take()[1]
            take()
            b = take()[1]
            c1, r1 = _col_row(a)
            c2, r2 = _col_row(b)
            return ("range", min(c1, c2), min(r1, r2), max(c1, c2), max(r1, r2))
        return formula()

    def if_call():
        lhs = formula()
        op = take()[1]
        rhs = formula()
        take()  # ','
        then = formula()
        take()  # ','
        other = formula()
        take()  # ')'
        return ("if", op, lhs, rhs, then, other)

    def atom():
        kind, val = take()
        if kind == "num":
            return ("num", int(val))
        if kind == "cell":
            return ("ref", val)
        if kind == "op" and val == "(":
            node = formula()
            take()  # ')'
            return node
        if kind == "id":
            take()  # '('
            if val == "IF":
                return if_call()
            args = [arg()]
            while peek() == ("op", ","):
                take()
                args.append(arg())
            take()  # ')'
            return ("call", val, args)
        raise ValueError("bad token: %r" % (val,))

    return formula()


def _tdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))
    values = {}
    active = set()

    def get(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in active:
            return _CYCLE
        active.add(name)
        v = evaluate_content(cells[name])
        active.discard(name)
        values[name] = v
        return v

    def evaluate_content(content):
        s = content.strip()
        if not s.startswith("="):
            return int(s)
        return ev(_parse(s[1:]))

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
            a = ev(node[2])
            if isinstance(a, str):
                return a
            b = ev(node[3])
            if isinstance(b, str):
                return b
            op = node[1]
            if op == "+":
                return a + b
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            if b == 0:
                return _DIV0
            return _tdiv(a, b)
        if kind == "if":
            op, lhs, rhs, then, other = node[1], node[2], node[3], node[4], node[5]
            a = ev(lhs)
            if isinstance(a, str):
                return a
            b = ev(rhs)
            if isinstance(b, str):
                return b
            return ev(then) if _CMP[op](a, b) else ev(other)
        if kind == "call":
            name, args = node[1], node[2]
            vals = []
            for a in args:
                if a[0] == "range":
                    _, cmin, rmin, cmax, rmax = a
                    for r in range(rmin, rmax + 1):
                        for c in range(cmin, cmax + 1):
                            nm = chr(65 + c) + str(r)
                            if nm not in cells:
                                continue
                            v = get(nm)
                            if isinstance(v, str):
                                return v
                            vals.append(v)
                else:
                    v = ev(a)
                    if isinstance(v, str):
                        return v
                    vals.append(v)
            if name == "SUM":
                return sum(vals)
            if name == "MIN":
                return min(vals) if vals else 0
            return max(vals) if vals else 0
        raise ValueError("unknown node: %r" % (kind,))

    for name in cells:
        get(name)
    return {name: values[name] for name in cells}
