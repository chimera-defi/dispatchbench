RUNG = 3
FUNC = "calc"
SIGNATURE = "def calc(expr: str) -> int | str:"
STATEMENT = """\
Evaluate an integer expression and return its value as a Python `int`, or the string `"error"`.

Syntax: non-negative decimal integer literals, binary operators `+ - * / % ^`, unary minus, parentheses, and any number of spaces between tokens. Every input is syntactically valid.

Precedence, from tightest to loosest:
1. `^` (power), right-associative: `2^3^2` is `2^(3^2)` = 512.
2. Unary minus, which may repeat (`--3` is 3). It binds looser than `^`, so `-2^2` is `-(2^2)` = -4. The right operand of `^` may start with a unary minus: `2^-1` is `2^(-1)`.
3. `*`, `/`, `%`, left-associative.
4. `+`, `-`, left-associative.

Semantics, with exact integer arithmetic and no size limit:
- `a / b` divides and truncates toward zero: `-7 / 2` is -3.
- `a % b` is `a - b * (a / b)`, using the truncating `/` above: `-7 % 2` is -1, and `7 % -2` is 1.
- `a ^ b` with `b >= 0` is `a` to the power `b`, and `0^0` is 1.
- The whole result is `"error"` if any evaluated step divides or takes a remainder by zero, or raises to a negative power.

Examples:
- `calc("1 + 2 * 3")` returns `7`.
- `calc("-2^2")` returns `-4`.
- `calc("(-2)^2")` returns `4`.
- `calc("2^3^2")` returns `512`.
- `calc("-7 / 2")` returns `-3`.
- `calc("7 % -2")` returns `1`.
- `calc("10^20 / 3")` returns `33333333333333333333`.
- `calc("5 / (3 - 3)")` returns `"error"`.
- `calc("2^-1")` returns `"error"`.

Constraints: `1 <= len(expr) <= 10000`. Parenthesis nesting depth is at most 50. In every test, exponents stay small enough that the exact result has at most a few thousand digits."""


class _Err(Exception):
    pass


def _tdiv(a, b):
    if b == 0: raise _Err
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _pow(a, b):
    if b < 0: raise _Err
    return a ** b


def ref(expr):
    toks = []; i = 0
    while i < len(expr):
        c = expr[i]
        if c == " ": i += 1
        elif c.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit(): j += 1
            toks.append(int(expr[i:j])); i = j
        else:
            toks.append(c); i += 1
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def take():
        nonlocal pos; pos += 1; return toks[pos - 1]

    def atom():
        t = take()
        if t == "(":
            v = add(); take(); return v
        return t

    def power():  # atom ('^' unary)?
        b = atom()
        if peek() == "^":
            take(); return _pow(b, unary())
        return b

    def unary():
        if peek() == "-":
            take(); return -unary()
        return power()

    def mul():
        v = unary()
        while peek() in ("*", "/", "%"):
            op = take(); r = unary()
            if op == "*": v = v * r
            elif op == "/": v = _tdiv(v, r)
            else: v = v - r * _tdiv(v, r)
        return v

    def add():
        v = mul()
        while peek() in ("+", "-"):
            op = take(); r = mul(); v = v + r if op == "+" else v - r
        return v

    try:
        return add()
    except _Err:
        return "error"


def brute(expr):
    # Independent: Python's grammar has the same precedence once ^ becomes **; walk its AST with these semantics.
    import ast
    tree = ast.parse(expr.replace("^", "**").strip(), mode="eval")

    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.UnaryOp): return -ev(n.operand)
        a, b = ev(n.left), ev(n.right)
        if isinstance(n.op, ast.Add): return a + b
        if isinstance(n.op, ast.Sub): return a - b
        if isinstance(n.op, ast.Mult): return a * b
        if isinstance(n.op, ast.Pow):
            if b < 0: raise ZeroDivisionError
            return a ** b
        if b == 0: raise ZeroDivisionError
        q = int(__import__("fractions").Fraction(a, b))  # Fraction -> int truncates toward zero
        return q if isinstance(n.op, ast.Div) else a - b * q
    try:
        return ev(tree)
    except ZeroDivisionError:
        return "error"


def _expr(rng, depth, big=False):
    if depth == 0 or rng.random() < 0.25:
        return str(rng.choice([0, 1, 2, 3, 7, rng.randint(0, 99)] + ([10**rng.randint(15, 30)] if big else [])))
    r = rng.random()
    if r < 0.12:
        return "-" * rng.randint(1, 2) + _expr(rng, depth - 1, big)
    if r < 0.22:
        return "(" + _expr(rng, depth - 1, big) + ")"
    op = rng.choice("+-*/%^" if not big else "+-*/%")
    if op == "^":
        exp = rng.choice(["2", "3", "0", "-1", "(1)", "-0", "2^1"])
        base = rng.choice(["2", "-2", "3", "(" + _expr(rng, 1) + ")", "0"])
        return base + "^" + exp
    sp = lambda: " " * rng.randint(0, 2)
    return _expr(rng, depth - 1, big) + sp() + op + sp() + _expr(rng, depth - 1, big)


def small(rng):
    return (_expr(rng, rng.randint(1, 5)),)


def fixed():
    return [(e,) for e, _ in [(a[0], b) for a, b in EXAMPLES]] + [("0^0",), ("--3",), ("-2^-2",), ("2^3^2^0",), ("-(3)%(-2)",),
                                                                  ("100000000000000000001 / 7",), ("((((1))))",), ("0 % 5",), ("1/0*0",)]


def big(rng):
    e = "0"
    while True:
        part = _expr(rng, 4, big=True)
        if ref(part) == "error": continue
        nxt = e + " - (" + part + ")"
        if len(nxt) > 10000: break
        e = nxt
    return [(e,), ("(" * 50 + "-7" + ") / 2" * 50,)]


EXAMPLES = [(("1 + 2 * 3",), 7), (("-2^2",), -4), (("(-2)^2",), 4), (("2^3^2",), 512), (("-7 / 2",), -3), (("7 % -2",), 1),
            (("10^20 / 3",), 33333333333333333333), (("5 / (3 - 3)",), "error"), (("2^-1",), "error")]

WRONG = {
    "python_floor": """
def calc(expr):
    import ast
    t = ast.parse(expr.replace('^', '**'), mode='eval')
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.UnaryOp): return -ev(n.operand)
        a, b = ev(n.left), ev(n.right)
        o = type(n.op).__name__
        if o == 'Pow':
            if b < 0: raise ZeroDivisionError
            return a ** b
        return {'Add': a + b, 'Sub': a - b, 'Mult': a * b}.get(o) if o in ('Add', 'Sub', 'Mult') else (a // b if o == 'Div' else a % b)
    try: return ev(t)
    except ZeroDivisionError: return 'error'
""",
    "float_division": """
def calc(expr):
    import ast
    t = ast.parse(expr.replace('^', '**'), mode='eval')
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.UnaryOp): return -ev(n.operand)
        a, b = ev(n.left), ev(n.right)
        o = type(n.op).__name__
        if o == 'Add': return a + b
        if o == 'Sub': return a - b
        if o == 'Mult': return a * b
        if o == 'Pow':
            if b < 0: raise ZeroDivisionError
            return a ** b
        q = int(a / b)
        return q if o == 'Div' else a - b * q
    try: return ev(t)
    except ZeroDivisionError: return 'error'
""",
    "unary_binds_tighter": """
def calc(expr):
    import ast, re
    e = re.sub(r'(?<![0-9)])\\s*-\\s*(\\d+)', r' (-\\1)', expr)
    t = ast.parse(e.replace('^', '**'), mode='eval')
    def ev(n):
        if isinstance(n, ast.Expression): return ev(n.body)
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.UnaryOp): return -ev(n.operand)
        a, b = ev(n.left), ev(n.right)
        o = type(n.op).__name__
        if o == 'Add': return a + b
        if o == 'Sub': return a - b
        if o == 'Mult': return a * b
        if o == 'Pow':
            if b < 0: raise ZeroDivisionError
            return a ** b
        if b == 0: raise ZeroDivisionError
        q = abs(a) // abs(b) * (1 if (a >= 0) == (b >= 0) else -1)
        return q if o == 'Div' else a - b * q
    try: return ev(t)
    except ZeroDivisionError: return 'error'
""",
}
