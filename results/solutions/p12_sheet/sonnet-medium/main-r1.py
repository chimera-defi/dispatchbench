import re
import sys
import threading

_TOK = re.compile(r"\s*(\d+|[A-Z]+\d*|<>|<=|>=|[=<>+\-*/(),:])")


def _tokenize(s):
    toks = []
    pos = 0
    s = s.rstrip()
    while pos < len(s):
        m = _TOK.match(s, pos)
        toks.append(m.group(1))
        pos = m.end()
    return toks


class _Parser:
    def __init__(self, toks):
        self.t = toks
        self.p = 0

    def peek(self, k=0):
        i = self.p + k
        return self.t[i] if i < len(self.t) else None

    def next(self):
        v = self.t[self.p]
        self.p += 1
        return v

    def expr(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.next()
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.peek() in ("*", "/"):
            op = self.next()
            node = ("bin", op, node, self.unary())
        return node

    def unary(self):
        if self.peek() == "-":
            self.next()
            return ("neg", self.unary())
        return self.atom()

    def atom(self):
        t = self.next()
        if t.isdigit():
            return ("num", int(t))
        if t == "(":
            e = self.expr()
            self.next()
            return e
        if self.peek() == "(" and t in ("SUM", "MIN", "MAX", "IF"):
            self.next()
            if t == "IF":
                l = self.expr()
                op = self.next()
                r = self.expr()
                self.next()
                th = self.expr()
                self.next()
                el = self.expr()
                self.next()
                return ("if", op, l, r, th, el)
            args = []
            while True:
                if self.peek(1) == ":":
                    a = self.next()
                    self.next()
                    b = self.next()
                    args.append(("range", a, b))
                else:
                    args.append(self.expr())
                if self.next() == ")":
                    break
            return ("agg", t, args)
        return ("ref", t)


def _split(name):
    return ord(name[0]) - 65, int(name[1:])


def sheet(cells):
    result = {}

    def run():
        asts = {}
        values = {}
        busy = set()

        def is_err(v):
            return isinstance(v, str)

        def ref(name):
            if name not in cells:
                return 0
            if name in values:
                return values[name]
            if name in busy:
                return "#CYCLE!"
            busy.add(name)
            c = cells[name].strip()
            try:
                v = int(c)
            except ValueError:
                if name not in asts:
                    asts[name] = _Parser(_tokenize(c[1:])).expr()
                v = ev(asts[name])
            busy.discard(name)
            values[name] = v
            return v

        def ev(n):
            k = n[0]
            if k == "num":
                return n[1]
            if k == "ref":
                return ref(n[1])
            if k == "neg":
                v = ev(n[1])
                return v if is_err(v) else -v
            if k == "bin":
                a = ev(n[2])
                if is_err(a):
                    return a
                b = ev(n[3])
                if is_err(b):
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
                q = abs(a) // abs(b)
                return q if (a < 0) == (b < 0) else -q
            if k == "if":
                a = ev(n[2])
                if is_err(a):
                    return a
                b = ev(n[3])
                if is_err(b):
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
            # aggregate
            vals = []
            for a in n[2]:
                if a[0] == "range":
                    c1, r1 = _split(a[1])
                    c2, r2 = _split(a[2])
                    if c1 > c2:
                        c1, c2 = c2, c1
                    if r1 > r2:
                        r1, r2 = r2, r1
                    for r in range(r1, r2 + 1):
                        for c in range(c1, c2 + 1):
                            nm = chr(65 + c) + str(r)
                            if nm in cells:
                                v = ref(nm)
                                if is_err(v):
                                    return v
                                vals.append(v)
                else:
                    v = ev(a)
                    if is_err(v):
                        return v
                    vals.append(v)
            if not vals:
                return 0
            if n[1] == "SUM":
                return sum(vals)
            if n[1] == "MIN":
                return min(vals)
            return max(vals)

        for name in cells:
            result[name] = ref(name)

    sys.setrecursionlimit(1000000)
    threading.stack_size(512 * 1024 * 1024)
    th = threading.Thread(target=run)
    th.start()
    th.join()
    return {k: result[k] for k in cells}
