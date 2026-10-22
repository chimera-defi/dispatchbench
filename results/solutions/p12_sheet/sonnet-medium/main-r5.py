import re
import sys
import threading

_TOK = re.compile(r"\s*(\d+|[A-Z]+\d*|<>|<=|>=|[-+*/(),:=<>])")


def _tokenize(s):
    out = []
    pos = 0
    s = s.rstrip()
    while pos < len(s):
        m = _TOK.match(s, pos)
        out.append(m.group(1))
        pos = m.end()
    return out


class _Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def next(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def formula(self):
        left = self.term()
        while self.peek() in ("+", "-"):
            op = self.next()
            right = self.term()
            left = ("bin", op, left, right)
        return left

    def term(self):
        left = self.unary()
        while self.peek() in ("*", "/"):
            op = self.next()
            right = self.unary()
            left = ("bin", op, left, right)
        return left

    def unary(self):
        if self.peek() == "-":
            self.next()
            return ("neg", self.unary())
        return self.atom()

    def atom(self):
        tok = self.next()
        if tok == "(":
            e = self.formula()
            self.next()
            return e
        if tok.isdigit():
            return ("num", int(tok))
        if self.peek() == "(":
            self.next()
            if tok == "IF":
                l = self.formula()
                op = self.next()
                r = self.formula()
                self.next()
                a = self.formula()
                self.next()
                b = self.formula()
                self.next()
                return ("if", op, l, r, a, b)
            args = []
            while True:
                args.append(self.arg())
                sep = self.next()
                if sep == ")":
                    break
            return ("fn", tok, args)
        return ("ref", tok)

    def arg(self):
        t = self.t
        i = self.i
        if (i + 2 < len(t) and t[i + 1] == ":"
                and t[i][0].isalpha() and t[i][-1].isdigit()):
            a = self.next()
            self.next()
            b = self.next()
            return ("range", a, b)
        return self.formula()


def _div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def _solve(cells):
    values = {}
    progress = set()
    asts = {}

    def get(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in progress:
            return "#CYCLE!"
        progress.add(name)
        content = cells[name].strip()
        if content.startswith("="):
            ast = _Parser(_tokenize(content[1:])).formula()
            v = ev(ast)
        else:
            v = int(content)
        progress.discard(name)
        values[name] = v
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
            a = ev(n[2])
            if isinstance(a, str):
                return a
            b = ev(n[3])
            if isinstance(b, str):
                return b
            op = n[1]
            if op == "+":
                return a + b
            if op == "-":
                return a - b
            if op == "*":
                return a * b
            if b == 0:
                return "#DIV/0!"
            return _div(a, b)
        if k == "if":
            a = ev(n[2])
            if isinstance(a, str):
                return a
            b = ev(n[3])
            if isinstance(b, str):
                return b
            op = n[1]
            if op == "=":
                c = a == b
            elif op == "<>":
                c = a != b
            elif op == "<":
                c = a < b
            elif op == "<=":
                c = a <= b
            elif op == ">":
                c = a > b
            else:
                c = a >= b
            return ev(n[4] if c else n[5])
        # function
        vals = []
        for arg in n[2]:
            if arg[0] == "range":
                a, b = arg[1], arg[2]
                c1, c2 = sorted((ord(a[0]), ord(b[0])))
                r1, r2 = sorted((int(a[1:]), int(b[1:])))
                for r in range(r1, r2 + 1):
                    for c in range(c1, c2 + 1):
                        nm = chr(c) + str(r)
                        if nm in cells:
                            v = get(nm)
                            if isinstance(v, str):
                                return v
                            vals.append(v)
            else:
                v = ev(arg)
                if isinstance(v, str):
                    return v
                vals.append(v)
        if not vals:
            return 0
        f = n[1]
        if f == "SUM":
            return sum(vals)
        if f == "MIN":
            return min(vals)
        return max(vals)

    for name in cells:
        get(name)
    return {name: values[name] for name in cells}


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    result = {}
    err = []

    def run():
        try:
            result.update(_solve(cells))
        except BaseException as e:
            err.append(e)

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(1000000)
    threading.stack_size(512 * 1024 * 1024)
    t = threading.Thread(target=run)
    t.start()
    t.join()
    sys.setrecursionlimit(old_limit)
    if err:
        raise err[0]
    return result
