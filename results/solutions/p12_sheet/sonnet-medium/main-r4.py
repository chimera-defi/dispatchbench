import re
import sys
import threading

_TOK = re.compile(r'\s*(\d+|[A-Z]+\d*|<>|<=|>=|[-+*/(),:=<>])')


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
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def next(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def expr(self):
        left = self.term()
        while self.peek() in ('+', '-'):
            op = self.next()
            right = self.term()
            left = ('bin', op, left, right)
        return left

    def term(self):
        left = self.unary()
        while self.peek() in ('*', '/'):
            op = self.next()
            right = self.unary()
            left = ('bin', op, left, right)
        return left

    def unary(self):
        if self.peek() == '-':
            self.next()
            return ('neg', self.unary())
        return self.atom()

    def atom(self):
        tok = self.next()
        if tok == '(':
            e = self.expr()
            self.next()
            return e
        if tok.isdigit():
            return ('n', int(tok))
        if self.peek() == '(':
            self.next()
            if tok == 'IF':
                l = self.expr()
                op = self.next()
                r = self.expr()
                self.next()
                t = self.expr()
                self.next()
                e = self.expr()
                self.next()
                return ('if', op, l, r, t, e)
            args = []
            while True:
                args.append(self.arg())
                if self.next() == ')':
                    break
            return ('f', tok, args)
        return ('c', tok)

    def arg(self):
        tok = self.peek()
        if (tok and tok[0].isalpha() and tok[1:].isdigit()
                and self.i + 1 < len(self.t) and self.t[self.i + 1] == ':'):
            a = self.next()
            self.next()
            b = self.next()
            c1, r1 = ord(a[0]), int(a[1:])
            c2, r2 = ord(b[0]), int(b[1:])
            return ('r', min(c1, c2), max(c1, c2), min(r1, r2), max(r1, r2))
        return self.expr()


def _solve(cells):
    done = {}
    busy = set()

    def cell(name):
        if name not in cells:
            return 0
        if name in done:
            return done[name]
        if name in busy:
            return "#CYCLE!"
        busy.add(name)
        content = cells[name].strip()
        if content.startswith('='):
            v = ev(_Parser(_tokenize(content[1:])).expr())
        else:
            v = int(content)
        busy.discard(name)
        done[name] = v
        return v

    def ev(n):
        k = n[0]
        if k == 'n':
            return n[1]
        if k == 'c':
            return cell(n[1])
        if k == 'neg':
            v = ev(n[1])
            return v if isinstance(v, str) else -v
        if k == 'bin':
            a = ev(n[2])
            if isinstance(a, str):
                return a
            b = ev(n[3])
            if isinstance(b, str):
                return b
            op = n[1]
            if op == '+':
                return a + b
            if op == '-':
                return a - b
            if op == '*':
                return a * b
            if b == 0:
                return "#DIV/0!"
            q = abs(a) // abs(b)
            return q if (a < 0) == (b < 0) else -q
        if k == 'if':
            a = ev(n[2])
            if isinstance(a, str):
                return a
            b = ev(n[3])
            if isinstance(b, str):
                return b
            op = n[1]
            if op == '=':
                c = a == b
            elif op == '<>':
                c = a != b
            elif op == '<':
                c = a < b
            elif op == '<=':
                c = a <= b
            elif op == '>':
                c = a > b
            else:
                c = a >= b
            return ev(n[4] if c else n[5])
        # function
        vals = []
        for arg in n[2]:
            if arg[0] == 'r':
                _, c1, c2, r1, r2 = arg
                for r in range(r1, r2 + 1):
                    for c in range(c1, c2 + 1):
                        nm = chr(c) + str(r)
                        if nm in cells:
                            v = cell(nm)
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
        if f == 'SUM':
            return sum(vals)
        if f == 'MIN':
            return min(vals)
        return max(vals)

    return {name: cell(name) for name in cells}


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    res = {}
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(1000000)
    old_stack = threading.stack_size()
    threading.stack_size(512 * 1024 * 1024)

    def run():
        res.update(_solve(cells))

    t = threading.Thread(target=run)
    t.start()
    t.join()
    threading.stack_size(old_stack)
    sys.setrecursionlimit(old)
    return res
