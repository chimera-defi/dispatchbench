import operator
import re
import sys

_DIV0 = "#DIV/0!"
_CYCLE = "#CYCLE!"
_TOKEN = re.compile(r"\s*(?:(\d+)|([A-Z]+\d*)|(<>|<=|>=|[-+*/(),:<>=]))")
_CMP = {
    "=": operator.eq,
    "<>": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


def _is_cell(tok):
    return tok is not None and re.fullmatch(r"[A-Z]\d+", tok) is not None


def _tokenize(text):
    tokens = []
    pos = 0
    while True:
        m = _TOKEN.match(text, pos)
        if m is None:
            break
        tokens.append(m.group(1) or m.group(2) or m.group(3))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, expected=None):
        tok = self.peek()
        if expected is not None and tok != expected:
            raise ValueError(f"expected {expected!r}, got {tok!r}")
        self.i += 1
        return tok

    def formula(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            node = ("bin", op, node, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.peek() in ("*", "/"):
            op = self.take()
            node = ("bin", op, node, self.unary())
        return node

    def unary(self):
        if self.peek() == "-":
            self.take()
            return ("neg", self.unary())
        return self.atom()

    def atom(self):
        tok = self.take()
        if tok is None:
            raise ValueError("unexpected end of formula")
        if tok.isdigit():
            return ("num", int(tok))
        if tok == "(":
            node = self.formula()
            self.take(")")
            return node
        if _is_cell(tok):
            return ("ref", tok)
        self.take("(")
        if tok == "IF":
            left = self.formula()
            op = self.take()
            if op not in _CMP:
                raise ValueError(f"bad comparison {op!r}")
            right = self.formula()
            self.take(",")
            then = self.formula()
            self.take(",")
            els = self.formula()
            self.take(")")
            return ("if", op, left, right, then, els)
        args = [self.arg()]
        while self.peek() == ",":
            self.take()
            args.append(self.arg())
        self.take(")")
        return ("call", tok, args)

    def arg(self):
        if _is_cell(self.peek()) and self.i + 1 < len(self.t) and self.t[self.i + 1] == ":":
            first = self.take()
            self.take(":")
            second = self.take()
            return ("range", first, second)
        return self.formula()


def _parse(text):
    return _Parser(_tokenize(text)).formula()


def _range_cells(a, b):
    col_a, row_a = ord(a[0]), int(a[1:])
    col_b, row_b = ord(b[0]), int(b[1:])
    for r in range(min(row_a, row_b), max(row_a, row_b) + 1):
        for c in range(min(col_a, col_b), max(col_a, col_b) + 1):
            yield f"{chr(c)}{r}"


def _trunc_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))
    memo = {}
    active = set()

    def cell_value(ref):
        if ref not in cells:
            return 0
        if ref in memo:
            return memo[ref]
        if ref in active:
            return _CYCLE
        active.add(ref)
        content = cells[ref].strip()
        if content.startswith("="):
            v = evaluate(_parse(content[1:]))
        else:
            v = int(content)
        active.discard(ref)
        memo[ref] = v
        return v

    def evaluate(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            v = evaluate(node[1])
            return v if isinstance(v, str) else -v
        if kind == "bin":
            op = node[1]
            left = evaluate(node[2])
            if isinstance(left, str):
                return left
            right = evaluate(node[3])
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
            return _trunc_div(left, right)
        if kind == "if":
            op, left_node, right_node, then_node, else_node = node[1], node[2], node[3], node[4], node[5]
            left = evaluate(left_node)
            if isinstance(left, str):
                return left
            right = evaluate(right_node)
            if isinstance(right, str):
                return right
            return evaluate(then_node if _CMP[op](left, right) else else_node)

        func, args = node[1], node[2]
        vals = []
        for arg in args:
            if arg[0] == "range":
                for ref in _range_cells(arg[1], arg[2]):
                    if ref not in cells:
                        continue
                    v = cell_value(ref)
                    if isinstance(v, str):
                        return v
                    vals.append(v)
            else:
                v = evaluate(arg)
                if isinstance(v, str):
                    return v
                vals.append(v)
        if func == "SUM":
            return sum(vals)
        if not vals:
            return 0
        return min(vals) if func == "MIN" else max(vals)

    return {name: cell_value(name) for name in cells}
