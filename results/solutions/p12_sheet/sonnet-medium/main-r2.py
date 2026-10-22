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
            return ('num', int(tok))
        if tok[-1].isdigit():
            return ('cell', tok)
        # function
        self.next()  # (
        if tok == 'IF':
            l = self.expr()
            op = self.next()
            r = self.expr()
            self.next()
            a = self.expr()
            self.next()
            b = self.expr()
            self.next()
            return ('if', op, l, r, a, b)
        args = []
        while True:
            p = self.peek()
            if (p is not None and p[0].isalpha() and p[-1].isdigit()
                    and self.i + 1 < len(self.t) and self.t[self.i + 1] == ':'):
                a = self.next()
                self.next()
                b = self.next()
                args.append(('range', a, b))
            else:
                args.append(self.expr())
            if self.next() == ')':
                break
        return ('func', tok, args)


def _solve(cells):
    memo = {}
    inprog = set()

    def getcell(name):
        if name not in cells:
            return 0
        if name in memo:
            return memo[name]
        if name in inprog:
            return "#CYCLE!"
        inprog.add(name)
        c = cells[name].strip()
        if c.startswith('='):
            ast = _Parser(_tokenize(c[1:])).expr()
            v = ev(ast)
        else:
            v = int(c)
        inprog.discard(name)
        memo[name] = v
        return v

    def ev(n):
        k = n[0]
        if k == 'num':
            return n[1]
        if k == 'cell':
            return getcell(n[1])
        if k == 'neg':
            v = ev(n[1])
            return v if isinstance(v, str) else -v
        if k == 'bin':
            l = ev(n[2])
            if isinstance(l, str):
                return l
            r = ev(n[3])
            if isinstance(r, str):
                return r
            op = n[1]
            if op == '+':
                return l + r
            if op == '-':
                return l - r
            if op == '*':
                return l * r
            if r == 0:
                return "#DIV/0!"
            q = abs(l) // abs(r)
            return -q if (l < 0) != (r < 0) else q
        if k == 'if':
            l = ev(n[2])
            if isinstance(l, str):
                return l
            r = ev(n[3])
            if isinstance(r, str):
                return r
            op = n[1]
            if op == '=':
                ok = l == r
            elif op == '<>':
                ok = l != r
            elif op == '<':
                ok = l < r
            elif op == '<=':
                ok = l <= r
            elif op == '>':
                ok = l > r
            else:
                ok = l >= r
            return ev(n[4] if ok else n[5])
        # func
        name = n[1]
        vals = []
        for a in n[2]:
            if a[0] == 'range':
                c1, c2 = a[1][0], a[2][0]
                r1, r2 = int(a[1][1:]), int(a[2][1:])
                for r in range(min(r1, r2), max(r1, r2) + 1):
                    for c in range(ord(min(c1, c2)), ord(max(c1, c2)) + 1):
                        nm = chr(c) + str(r)
                        if nm in cells:
                            v = getcell(nm)
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
        if name == 'SUM':
            return sum(vals)
        if name == 'MIN':
            return min(vals)
        return max(vals)

    for name in cells:
        getcell(name)
    return {name: memo[name] for name in cells}


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    result = []
    err = []

    def run():
        try:
            result.append(_solve(cells))
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
    return result[0]
