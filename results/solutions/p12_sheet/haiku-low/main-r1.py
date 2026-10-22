import re

_CELL_RE = re.compile(r'^[A-Z](?:[1-9]|[1-9][0-9])$')


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    DIV0 = "#DIV/0!"
    CYCLE = "#CYCLE!"

    state = {}   # name -> 'busy' or 'done'
    values = {}  # name -> computed value

    def cell_value(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if state.get(name) == 'busy':
            return CYCLE
        state[name] = 'busy'
        v = evaluate_content(cells[name].strip())
        state[name] = 'done'
        values[name] = v
        return v

    def tokenize(s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c.isspace():
                i += 1
            elif c.isdigit():
                j = i
                while j < n and s[j].isdigit():
                    j += 1
                tokens.append(('NUM', int(s[i:j])))
                i = j
            elif c.isalpha():
                j = i
                while j < n and s[j].isalpha():
                    j += 1
                k = j
                while k < n and s[k].isdigit():
                    k += 1
                if k > j:
                    tokens.append(('REF', s[i:k]))
                    i = k
                else:
                    tokens.append(('ID', s[i:j].upper()))
                    i = j
            elif s[i:i + 2] in ('<>', '<=', '>='):
                tokens.append(('OP', s[i:i + 2]))
                i += 2
            elif c in '+-*/():,<>=':
                tokens.append(('OP', c))
                i += 1
            else:
                raise ValueError("bad char")
        tokens.append(('EOF', None))
        return tokens

    def evaluate_content(content):
        if content.startswith('='):
            return eval_formula_text(content[1:])
        return int(content)

    def eval_formula_text(text):
        p = Parser(tokenize(text))
        return p.parse_formula_top()

    class Err(Exception):
        def __init__(self, val):
            self.val = val

    class Parser:
        def __init__(self, toks):
            self.toks = toks
            self.pos = 0

        def peek(self):
            return self.toks[self.pos]

        def next(self):
            t = self.toks[self.pos]
            self.pos += 1
            return t

        def is_op(self, sym):
            t = self.peek()
            return t[0] == 'OP' and t[1] == sym

        def expect_op(self, sym):
            if not self.is_op(sym):
                raise ValueError("expected " + sym)
            self.pos += 1

        # Parsing produces a thunk-free AST would be ideal, but the
        # short-circuit rules require lazy evaluation. We therefore
        # parse into nodes and evaluate them on demand.

        def parse_formula_top(self):
            node = self.parse_additive()
            if self.peek()[0] != 'EOF':
                raise ValueError("trailing tokens")
            return evaluate(node)

        # ---- AST builders ----
        def parse_additive(self):
            node = self.parse_term()
            while self.is_op('+') or self.is_op('-'):
                op = self.next()[1]
                rhs = self.parse_term()
                node = ('bin', op, node, rhs)
            return node

        def parse_term(self):
            node = self.parse_unary()
            while self.is_op('*') or self.is_op('/'):
                op = self.next()[1]
                rhs = self.parse_unary()
                node = ('bin', op, node, rhs)
            return node

        def parse_unary(self):
            if self.is_op('-'):
                self.next()
                return ('neg', self.parse_unary())
            return self.parse_atom()

        def parse_atom(self):
            t = self.peek()
            if t[0] == 'NUM':
                self.next()
                return ('num', t[1])
            if t[0] == 'REF':
                self.next()
                return ('ref', t[1])
            if t[0] == 'OP' and t[1] == '(':
                self.next()
                node = self.parse_additive()
                self.expect_op(')')
                return node
            if t[0] == 'ID':
                name = t[1]
                self.next()
                self.expect_op('(')
                if name == 'IF':
                    left = self.parse_additive()
                    op = self.next()
                    if op[0] != 'OP' or op[1] not in ('=', '<>', '<', '<=', '>', '>='):
                        raise ValueError("bad comparison")
                    right = self.parse_additive()
                    self.expect_op(',')
                    then = self.parse_additive()
                    self.expect_op(',')
                    els = self.parse_additive()
                    self.expect_op(')')
                    return ('if', op[1], left, right, then, els)
                args = []
                while True:
                    if self.peek()[0] == 'REF' and self.toks[self.pos + 1] == ('OP', ':'):
                        pass
                    args.append(self.parse_arg())
                    if self.is_op(','):
                        self.next()
                        continue
                    break
                self.expect_op(')')
                return ('func', name, args)
            raise ValueError("unexpected token")

        def parse_arg(self):
            # range X1:Y2 or formula
            if self.peek()[0] == 'REF':
                save = self.pos
                first = self.next()[1]
                if self.is_op(':'):
                    self.next()
                    if self.peek()[0] == 'REF':
                        second = self.next()[1]
                        return ('range', first, second)
                self.pos = save
            return self.parse_additive()

    def split_ref(name):
        m = re.match(r'^([A-Z])([0-9]+)$', name)
        return m.group(1), int(m.group(2))

    def evaluate(node):
        kind = node[0]
        if kind == 'num':
            return node[1]
        if kind == 'ref':
            return cell_value(node[1])
        if kind == 'neg':
            v = evaluate(node[1])
            if isinstance(v, str):
                return v
            return -v
        if kind == 'bin':
            _, op, ln, rn = node
            lv = evaluate(ln)
            if isinstance(lv, str):
                return lv
            rv = evaluate(rn)
            if isinstance(rv, str):
                return rv
            if op == '+':
                return lv + rv
            if op == '-':
                return lv - rv
            if op == '*':
                return lv * rv
            if rv == 0:
                return DIV0
            q = abs(lv) // abs(rv)
            return q if (lv >= 0) == (rv >= 0) else -q
        if kind == 'if':
            _, op, ln, rn, then, els = node
            lv = evaluate(ln)
            if isinstance(lv, str):
                return lv
            rv = evaluate(rn)
            if isinstance(rv, str):
                return rv
            cond = {
                '=': lv == rv, '<>': lv != rv, '<': lv < rv,
                '<=': lv <= rv, '>': lv > rv, '>=': lv >= rv,
            }[op]
            return evaluate(then if cond else els)
        if kind == 'func':
            _, name, args = node
            vals = []
            for a in args:
                if a[0] == 'range':
                    c1, r1 = split_ref(a[1])
                    c2, r2 = split_ref(a[2])
                    cl, ch = sorted((ord(c1), ord(c2)))
                    rl, rh = sorted((r1, r2))
                    for r in range(rl, rh + 1):
                        for c in range(cl, ch + 1):
                            nm = chr(c) + str(r)
                            if nm not in cells:
                                continue
                            v = cell_value(nm)
                            if isinstance(v, str):
                                return v
                            vals.append(v)
                else:
                    v = evaluate(a)
                    if isinstance(v, str):
                        return v
                    vals.append(v)
            if name == 'SUM':
                return sum(vals)
            if name == 'MIN':
                return min(vals) if vals else 0
            if name == 'MAX':
                return max(vals) if vals else 0
            raise ValueError("unknown function")
        raise ValueError("bad node")

    result = {}
    for name in cells:
        result[name] = cell_value(name)
    return result
