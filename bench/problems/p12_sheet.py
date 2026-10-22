RUNG = 6
FUNC = "sheet"
SIGNATURE = "def sheet(cells: dict[str, str]) -> dict[str, int | str]:"
STATEMENT = """\
Evaluate a small spreadsheet. `cells` maps cell names to contents. A cell name is one column letter `A`..`Z` followed by a row number `1`..`99` with no leading zero, for example `B12`. Return a dict mapping every name in `cells` to its value. A value is an integer, or one of the error strings `"#DIV/0!"` and `"#CYCLE!"`.

Contents:
- An integer literal such as `42` or `-7` is that integer.
- Otherwise the content starts with `=` and the rest is a formula. Spaces may appear between any two tokens.

Formula grammar, from lowest to highest precedence:
- `+` and `-`, left-associative;
- `*` and `/`, left-associative;
- unary minus (it may repeat, as in `--3`);
- atoms: a non-negative integer, a cell name, `( formula )`, a function call.

Functions:
- `SUM(...)`, `MIN(...)` and `MAX(...)` take one or more comma-separated arguments. Each argument is either a range `X1:Y2` (the rectangle with those two corners, in either order) or a formula.
- `IF(left OP right, then, else)`, where `OP` is one of `=`, `<>`, `<`, `<=`, `>`, `>=`, and `left`, `right`, `then`, `else` are formulas.

Semantics:
1. All arithmetic is on unbounded integers. `/` divides and truncates toward zero (`-7/2` is `-3`). Dividing by zero gives `#DIV/0!`.
2. A reference to a cell that is not in `cells` has value `0`.
3. Inside a range, cells that are not in `cells` are skipped. `MIN` and `MAX` with no values at all give `0`, and `SUM` with no values gives `0`. Formula arguments are never skipped: a formula argument that is a missing cell, such as `MIN(Z9)`, contributes `0`.
4. Errors propagate, and evaluation goes strictly left to right and stops at the first error. For a binary operator, if the left operand is an error the result is that error and the right operand is not evaluated; otherwise the right operand is evaluated next. Function arguments are evaluated left to right, and the cells of a range in row-major order: top row first, left to right within a row. The first error met is the result.
5. `IF` evaluates `left`, then `right`. If either is an error the result is that error. Otherwise only the chosen branch is evaluated. The other branch is never evaluated, so errors and references inside it have no effect.
6. A reference to a cell whose own evaluation is still in progress has value `#CYCLE!`. Each cell is evaluated at most once; once it has a value, later references reuse that value.

Examples:
- `sheet({"A1": "5", "A2": "=A1 * 2 + B9", "B1": "=-7/2"})` returns `{"A1": 5, "A2": 10, "B1": -3}`.
- `sheet({"A1": "=IF(A2 = 0, 1, A1)", "A2": "0"})` returns `{"A1": 1, "A2": 0}`.
- `sheet({"A1": "=A2 + B1", "A2": "=1/0", "B1": "=A1"})` returns `{"A1": "#DIV/0!", "A2": "#DIV/0!", "B1": "#DIV/0!"}`.
- `sheet({"A1": "=B1", "B1": "=A1 + 1", "C1": "=MAX(A1:B3, 2)"})` returns `{"A1": "#CYCLE!", "B1": "#CYCLE!", "C1": "#CYCLE!"}`.
- `sheet({"A1": "=MIN(B1:B3)", "B2": "4", "C1": "=MAX(D1:D5) + MIN(Z9)"})` returns `{"A1": 4, "B2": 4, "C1": 0}`.

Constraints: at most 2574 cells (every cell from `A1` to `Z99`). Every formula is valid and refers only to cells `A1`..`Z99`. A chain of references can pass through every cell. Cell names in ranges are always valid."""

_SRC = r'''
import re, sys
_TOKEN = re.compile(r"\d+|[A-Z]+\d*|<=|>=|<>|[-+*/(),:=<>]")
_CELL = re.compile(r"[A-Z]\d+")


def _parse(text):
    toks = _TOKEN.findall(text); pos = 0

    def peek(o=0):
        return toks[pos + o] if pos + o < len(toks) else None

    def take():
        nonlocal pos
        pos += 1
        return toks[pos - 1]

    def expr():
        node = term()
        while peek() in ("+", "-"):
            op = take(); node = ("bin", op, node, term())
        return node

    def term():
        node = unary()
        while peek() in ("*", "/"):
            op = take(); node = ("bin", op, node, unary())
        return node

    def unary():
        if peek() == "-":
            take(); return ("neg", unary())
        return atom()

    def atom():
        t = take()
        if t == "(":
            node = expr(); take(); return node
        if t.isdigit():
            return ("num", int(t))
        if t == "IF":
            take(); a = expr(); op = take(); b = expr(); take(); x = expr(); take(); y = expr(); take()
            return ("if", a, op, b, x, y)
        if t in ("SUM", "MIN", "MAX"):
            take(); args = []
            while True:
                if _CELL.fullmatch(peek() or "") and peek(1) == ":":
                    a = take(); take(); args.append(("range", a, take()))
                else:
                    args.append(expr())
                if take() == ")":
                    return ("fn", t, args)
        return ("ref", t)
    return expr()


def _rect(a, b):
    c1, c2 = sorted((ord(a[0]), ord(b[0]))); r1, r2 = sorted((int(a[1:]), int(b[1:])))
    return [f"{chr(c)}{r}" for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def sheet(cells):
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))  # RECURSION
    asts = {n: (_parse(t[1:]) if t.startswith("=") else ("num", int(t))) for n, t in cells.items()}
    memo, busy = {}, set()

    def cell(n):
        if n not in asts: return 0
        if n in memo: return memo[n]
        if n in busy: return "#CYCLE!"
        busy.add(n); v = ev(asts[n]); busy.discard(n); memo[n] = v
        return v

    def ev(node):
        k = node[0]
        if k == "num": return node[1]
        if k == "ref": return cell(node[1])
        if k == "neg":
            x = ev(node[1])
            return x if isinstance(x, str) else -x
        if k == "bin":
            _, op, a, b = node
            x = ev(a)  # LEFT
            if isinstance(x, str): return x
            y = ev(b)  # RIGHT
            if isinstance(y, str): return y
            if op == "+": return x + y
            if op == "-": return x - y
            if op == "*": return x * y
            if y == 0: return "#DIV/0!"
            q = abs(x) // abs(y)  # DIVISION
            return q if (x < 0) == (y < 0) else -q
        if k == "if":
            _, a, op, b, t, f = node
            x = ev(a)
            if isinstance(x, str): return x
            y = ev(b)
            if isinstance(y, str): return y
            ok = {"=": x == y, "<>": x != y, "<": x < y, "<=": x <= y, ">": x > y, ">=": x >= y}[op]
            return ev(t if ok else f)  # BRANCH
        _, fn, args = node; vals = []
        for arg in args:
            if arg[0] == "range":
                for n in _rect(arg[1], arg[2]):
                    if n in asts:  # SKIP
                        v = cell(n)
                        if isinstance(v, str): return v
                        vals.append(v)
            else:
                v = ev(arg)
                if isinstance(v, str): return v
                vals.append(v)
        if fn == "SUM": return sum(vals)
        if not vals: return 0
        return min(vals) if fn == "MIN" else max(vals)

    return {n: cell(n) for n in cells}
'''

_ns = {}
exec(_SRC, _ns)
ref = _ns["sheet"]


def brute(cells):
    # Independent: character scanner, precedence climbing that evaluates while parsing (with a live flag for
    # branches that must not run), errors as exceptions, cells driven in reverse input order.
    class Err(Exception):
        pass

    val, busy = {}, set()

    def lex(s):
        out, i = [], 0
        while i < len(s):
            ch = s[i]
            if ch == " ": i += 1; continue
            if ch.isdigit():
                j = i
                while j < len(s) and s[j].isdigit(): j += 1
                out.append(("n", int(s[i:j]))); i = j; continue
            if ch.isalpha():
                j = i
                while j < len(s) and s[j].isalpha(): j += 1
                k = j
                while k < len(s) and s[k].isdigit(): k += 1
                out.append(("c", s[i:k]) if k > j else ("f", s[i:j])); i = k; continue
            if s[i:i + 2] in ("<=", ">=", "<>"): out.append(("o", s[i:i + 2])); i += 2; continue
            out.append(("o", ch)); i += 1
        return out

    def get(c):
        if c not in cells: return 0
        if c in val:
            if isinstance(val[c], str): raise Err(val[c])
            return val[c]
        if c in busy: raise Err("#CYCLE!")
        busy.add(c); t = cells[c]
        try:
            v = evaluate(lex(t[1:])) if t.startswith("=") else int(t)
        except Err as e:
            v = str(e)
        busy.discard(c); val[c] = v
        if isinstance(v, str): raise Err(v)
        return v

    def tdiv(x, y):
        if y == 0: raise Err("#DIV/0!")
        q = x // y
        if q < 0 and q * y != x: q += 1
        return q

    def evaluate(toks):
        pos = [0]; PREC = {"+": 1, "-": 1, "*": 2, "/": 2}
        peek = lambda o=0: toks[pos[0] + o] if pos[0] + o < len(toks) else ("o", "$")

        def nxt():
            t = peek(); pos[0] += 1; return t

        def primary(live):
            t = nxt()
            if t == ("o", "-"):
                v = primary(live); return -v if live else None
            if t == ("o", "("):
                v = climb(1, live); nxt(); return v
            if t[0] == "n": return t[1]
            if t[0] == "c": return get(t[1]) if live else None
            name = t[1]; nxt()
            if name == "IF":
                a = climb(1, live); op = nxt()[1]; b = climb(1, live); nxt()
                cond = live and {"=": a == b, "<>": a != b, "<": live and a < b, "<=": live and a <= b,
                                 ">": live and a > b, ">=": live and a >= b}[op]
                x = climb(1, live and cond); nxt(); y = climb(1, live and not cond); nxt()
                return (x if cond else y) if live else None
            vals = []
            while True:
                if peek()[0] == "c" and peek(1) == ("o", ":"):
                    a = nxt()[1]; nxt(); b = nxt()[1]
                    if live:
                        ca, cb = sorted([a[0], b[0]]); ra, rb = sorted([int(a[1:]), int(b[1:])])
                        for r in range(ra, rb + 1):
                            for c in range(ord(ca), ord(cb) + 1):
                                nm = chr(c) + str(r)
                                if nm in cells: vals.append(get(nm))
                else:
                    v = climb(1, live)
                    if live: vals.append(v)
                if nxt() == ("o", ")"): break
            if not live: return None
            if name == "SUM": return sum(vals)
            return (min(vals) if name == "MIN" else max(vals)) if vals else 0

        def climb(minp, live):
            x = primary(live)
            while peek()[0] == "o" and PREC.get(peek()[1], 0) >= minp:
                op = nxt()[1]; y = climb(PREC[op] + 1, live)
                if live:
                    x = x + y if op == "+" else x - y if op == "-" else x * y if op == "*" else tdiv(x, y)
            return x
        return climb(1, True)

    for c in reversed(list(cells)):
        try: get(c)
        except Err: pass
    return {c: val[c] for c in cells}


def _sp(rng):
    return rng.choice(["", "", " "])


def _formula(rng, names, d):
    def atom(d):
        r = rng.random()
        if d <= 0 or r < 0.25: return str(rng.choice([0, 0, 1, 2, 3, 7, 10]))
        if r < 0.55: return rng.choice(names)
        if r < 0.65: return "(" + expr(d - 1) + ")"
        if r < 0.85:
            args = []
            for _ in range(rng.randint(1, 3)):
                if rng.random() < 0.6:
                    args.append(rng.choice(names) + ":" + rng.choice(names))
                else:
                    args.append(expr(d - 1))
            return rng.choice(["SUM", "MIN", "MAX"]) + "(" + ("," + _sp(rng)).join(args) + ")"
        op = rng.choice(["=", "<>", "<", "<=", ">", ">="])
        return f"IF({expr(d - 1)}{_sp(rng)}{op}{_sp(rng)}{expr(d - 1)},{_sp(rng)}{expr(d - 1)},{_sp(rng)}{expr(d - 1)})"

    def unary(d):
        return ("-" if rng.random() < 0.15 else "") + atom(d)

    def term(d):
        s = unary(d)
        for _ in range(rng.choice([0, 0, 1, 2])):
            s += _sp(rng) + rng.choice(["*", "/", "/"]) + _sp(rng) + unary(d)
        return s

    def expr(d):
        s = term(d)
        for _ in range(rng.choice([0, 1, 1, 2])):
            s += _sp(rng) + rng.choice(["+", "-"]) + _sp(rng) + term(d)
        return s
    return "=" + expr(d)


def small(rng):
    names = [c + str(r) for r in range(1, 5) for c in "ABC"]
    cells = {}
    for n in rng.sample(names, len(names)):
        if rng.random() < 0.7:
            cells[n] = str(rng.randint(-9, 9)) if rng.random() < 0.3 else _formula(rng, names, rng.randint(1, 3))
    return (cells,)


def fixed():
    return [a for a, _ in EXAMPLES] + [
        ({"A1": "=--3 - -2"},), ({"A1": "=7/-2", "A2": "=-7/-2", "A3": "=0/5"},),
        ({"A1": "=IF(1 > 0, 5, 1/0)", "A2": "=IF(1 > 2, A2, B2)", "B2": "=A2"},),
        ({"A1": "=SUM(C3:A1)", "B2": "=1/0", "C1": "=A1"},), ({"A1": "=A1"},),
        ({"B1": "=A1 + 1/0", "A1": "=B1"},), ({"A1": "=MIN(B1:B2, C1)", "B1": "-5"},),
        ({"A1": "=IF(A1 = 0, 1, 2)"},), ({"A1": "=SUM(A1:A1)"},), ({"Z99": "=Z98*2", "Z98": "=MAX(  Y1 : Z3 ) - 4"},),
        ({"A1": "=IF(A2=0, 1, B1)", "B1": "=A1+1", "A2": "0"},), ({"C3": "=IF(1<2, 0, SUM(A1:B2))", "A1": "=C3 * 2"},),
        ({"B2": "=MIN(A1, IF(A1 <> 0, 3, C1))", "A1": "=IF(A1 = A1, 4, 5)", "C1": "=B2"},),
    ]


_ALL = [c + str(r) for r in range(1, 100) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]


def big(rng):
    out = []
    chain = {n: f"={_ALL[i + 1]} {rng.choice(['+', '-'])} {rng.randint(0, 9)}" for i, n in enumerate(_ALL[:-1])}
    chain[_ALL[-1]] = "7"; out.append((chain,))
    ring = {n: f"={_ALL[(i + 1) % len(_ALL)]} + 1" for i, n in enumerate(_ALL)}; out.append((ring,))
    lazy = {n: f"=IF({_ALL[i + 1]} >= 0, {_ALL[i + 1]} + 1, {_ALL[0]})" for i, n in enumerate(_ALL[:-1])}
    lazy[_ALL[-1]] = "0"; out.append((lazy,))
    grid = {}
    for idx, n in enumerate(_ALL):
        c, r = n[0], int(n[1:])
        if r == 99 or c == "Z":
            grid[n] = str(rng.randint(-50, 50)); continue
        c2 = chr(min(ord("Z"), ord(c) + rng.randint(1, 2))); r2 = min(99, r + rng.randint(1, 2))
        grid[n] = f"=MAX({c}{r + 1}:{c2}{r2}) - MIN({chr(ord(c) + 1)}{r}, {c2}{r2}) + {rng.randint(0, 3)}"
    out.append((dict(rng.sample(sorted(grid.items()), len(grid))),))
    rand = {}
    for n in rng.sample(_ALL, 2000):
        rand[n] = str(rng.randint(-9, 9)) if rng.random() < 0.25 else _formula(rng, _ALL, 2)
    out.append((rand,))
    return out


EXAMPLES = [(({"A1": "5", "A2": "=A1 * 2 + B9", "B1": "=-7/2"},), {"A1": 5, "A2": 10, "B1": -3}),
            (({"A1": "=IF(A2 = 0, 1, A1)", "A2": "0"},), {"A1": 1, "A2": 0}),
            (({"A1": "=A2 + B1", "A2": "=1/0", "B1": "=A1"},), {"A1": "#DIV/0!", "A2": "#DIV/0!", "B1": "#DIV/0!"}),
            (({"A1": "=B1", "B1": "=A1 + 1", "C1": "=MAX(A1:B3, 2)"},), {"A1": "#CYCLE!", "B1": "#CYCLE!", "C1": "#CYCLE!"}),
            (({"A1": "=MIN(B1:B3)", "B2": "4", "C1": "=MAX(D1:D5) + MIN(Z9)"},), {"A1": 4, "B2": 4, "C1": 0})]


def _variant(old, new):
    assert old in _SRC, old
    return _SRC.replace(old, new)


WRONG = {
    "if_as_function": _variant("return ev(t if ok else f)  # BRANCH",
                               "tv = ev(t)\n            if isinstance(tv, str): return tv\n            fv = ev(f)\n            if isinstance(fv, str): return fv\n            return tv if ok else fv"),
    "eager_if_keeps_chosen": _variant("return ev(t if ok else f)  # BRANCH",
                                      "tv, fv = ev(t), ev(f)\n            return tv if ok else fv"),
    "floor_division": _variant("q = abs(x) // abs(y)  # DIVISION\n            return q if (x < 0) == (y < 0) else -q", "return x // y"),
    "evaluate_both_operands": _variant("x = ev(a)  # LEFT\n            if isinstance(x, str): return x\n            y = ev(b)  # RIGHT",
                                       "x = ev(a); y = ev(b)\n            if isinstance(x, str): return x"),
    "range_missing_as_zero": _variant("if n in asts:  # SKIP", "if True:"),
    "default_recursion_limit": _variant("sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))  # RECURSION", "pass"),
}
