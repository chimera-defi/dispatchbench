import re
import sys
import threading

ERR_DIV = "#DIV/0!"
ERR_CYC = "#CYCLE!"
_TOKEN = re.compile(r"[A-Z]\d+|[A-Z]+|\d+|<>|<=|>=|[-+*/(),:=<>]")
_CELL = re.compile(r"[A-Z]\d+")
_IDENT = re.compile(r"[A-Z]+")


def _split(ref):
    m = re.fullmatch(r"([A-Z])(\d+)", ref)
    return ord(m.group(1)), int(m.group(2))


def _parse(src):
    toks = _TOKEN.findall(re.sub(r"\s+", "", src))
    pos = [0]

    def peek(k=0):
        j = pos[0] + k
        return toks[j] if j < len(toks) else None

    def take(expected=None):
        t = peek()
        if expected is not None and t != expected:
            raise ValueError(f"expected {expected!r}, got {t!r}")
        pos[0] += 1
        return t

    def formula():
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
        t = peek()
        if t is None:
            raise ValueError("unexpected end of formula")
        if t == "(":
            take()
            node = formula()
            take(")")
            return node
        if t.isdigit():
            take()
            return ("num", int(t))
        if _CELL.fullmatch(t):
            take()
            return ("ref", t)
        if _IDENT.fullmatch(t):
            take()
            take("(")
            return call(t)
        raise ValueError(f"unexpected token {t!r}")

    def call(name):
        if name == "IF":
            left = formula()
            op = take()
            right = formula()
            take(",")
            then = formula()
            take(",")
            other = formula()
            take(")")
            return ("if", op, left, right, then, other)
        args = [arg()]
        while peek() == ",":
            take()
            args.append(arg())
        take(")")
        return ("func", name, args)

    def arg():
        if peek() is not None and _CELL.fullmatch(peek()) and peek(1) == ":":
            a = take()
            take(":")
            b = take()
            return ("range", a, b)
        return formula()

    tree = formula()
    if pos[0] != len(toks):
        raise ValueError("trailing tokens")
    return tree


def _evaluate(cells):
    memo = {}
    active = set()

    def get(name):
        if name not in cells:
            return 0
        if name in memo:
            return memo[name]
        if name in active:
            return ERR_CYC
        active.add(name)
        raw = cells[name].strip()
        if raw.startswith("="):
            v = ev(_parse(raw[1:]))
        else:
            v = int(raw)
        active.discard(name)
        memo[name] = v
        return v

    def ev(n):
        k = n[0]
        if k == "num":
            return n[1]
        if k == "ref":
            return get(n[1])
        if k == "neg":
            v = ev(n[1])
            return v if isinstance(v, str) else -v
        if k == "bin":
            l = ev(n[2])
            if isinstance(l, str):
                return l
            r = ev(n[3])
            if isinstance(r, str):
                return r
            op = n[1]
            if op == "+":
                return l + r
            if op == "-":
                return l - r
            if op == "*":
                return l * r
            if r == 0:
                return ERR_DIV
            q = abs(l) // abs(r)
            return q if (l < 0) == (r < 0) else -q
        if k == "if":
            l = ev(n[2])
            if isinstance(l, str):
                return l
            r = ev(n[3])
            if isinstance(r, str):
                return r
            ok = {
                "=": l == r,
                "<>": l != r,
                "<": l < r,
                "<=": l <= r,
                ">": l > r,
                ">=": l >= r,
            }[n[1]]
            return ev(n[4]) if ok else ev(n[5])
        if k == "func":
            vals = []
            for a in n[2]:
                if a[0] == "range":
                    c1, r1 = _split(a[1])
                    c2, r2 = _split(a[2])
                    for r in range(min(r1, r2), max(r1, r2) + 1):
                        for c in range(min(c1, c2), max(c1, c2) + 1):
                            name = chr(c) + str(r)
                            if name not in cells:
                                continue
                            v = get(name)
                            if isinstance(v, str):
                                return v
                            vals.append(v)
                else:
                    v = ev(a)
                    if isinstance(v, str):
                        return v
                    vals.append(v)
            if n[1] == "SUM":
                return sum(vals)
            if n[1] == "MIN":
                return min(vals) if vals else 0
            return max(vals) if vals else 0
        raise ValueError(f"unknown node {k!r}")

    return {name: get(name) for name in cells}


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    result = {}
    errors = []

    def run():
        try:
            result.update(_evaluate(cells))
        except BaseException as e:
            errors.append(e)

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 1_000_000))
    old_size = threading.stack_size(256 * 1024 * 1024)
    try:
        t = threading.Thread(target=run)
        t.start()
        t.join()
    finally:
        threading.stack_size(old_size)
        sys.setrecursionlimit(old_limit)

    if errors:
        raise errors[0]
    return result
