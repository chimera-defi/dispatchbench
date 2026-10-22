import re
import sys
import threading

_CELL = re.compile(r"[A-Z]\d+")
_INT = re.compile(r"-?\d+")
_TOKEN = re.compile(r"\d+|[A-Z]+\d*|<>|<=|>=|[-+*/(),:=<>]")
_DIV0 = "#DIV/0!"
_CYCLE = "#CYCLE!"


class _Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expr(self):
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
        if tok == "(":
            node = self.expr()
            self.take()  # ')'
            return node
        if tok.isdigit():
            return ("num", int(tok))
        if _CELL.fullmatch(tok):
            return ("ref", tok)
        # Function call: name followed by '(' ... ')'
        self.take()  # '('
        if tok == "IF":
            left = self.expr()
            op = self.take()
            right = self.expr()
            self.take()  # ','
            then = self.expr()
            self.take()  # ','
            other = self.expr()
            self.take()  # ')'
            return ("if", op, left, right, then, other)
        args = [self.arg()]
        while self.peek() == ",":
            self.take()
            args.append(self.arg())
        self.take()  # ')'
        return ("func", tok, args)

    def arg(self):
        nxt = self.i + 1
        if nxt < len(self.t) and self.t[nxt] == ":" and _CELL.fullmatch(self.peek() or ""):
            c1 = self.take()
            self.take()  # ':'
            c2 = self.take()
            return ("range", c1, c2)
        return ("expr", self.expr())


def _parse_content(text):
    s = text.strip()
    if _INT.fullmatch(s):
        return ("num", int(s))
    body = s[1:] if s.startswith("=") else s
    tokens = _TOKEN.findall(body.upper())
    return _Parser(tokens).expr()


def _range_cells(c1, c2):
    col1, row1 = c1[0], int(c1[1:])
    col2, row2 = c2[0], int(c2[1:])
    cols = range(min(ord(col1), ord(col2)), max(ord(col1), ord(col2)) + 1)
    rows = range(min(row1, row2), max(row1, row2) + 1)
    for r in rows:
        for c in cols:
            yield f"{chr(c)}{r}"


def _solve(cells):
    parsed = {name: _parse_content(content) for name, content in cells.items()}
    values = {}
    in_progress = set()

    def ref(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in in_progress:
            return _CYCLE
        in_progress.add(name)
        v = ev(parsed[name])
        in_progress.discard(name)
        values[name] = v
        return v

    def ev(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return ref(node[1])
        if kind == "neg":
            v = ev(node[1])
            return v if isinstance(v, str) else -v
        if kind == "bin":
            left = ev(node[2])
            if isinstance(left, str):
                return left
            right = ev(node[3])
            if isinstance(right, str):
                return right
            op = node[1]
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if right == 0:
                return _DIV0
            q = abs(left) // abs(right)
            return q if (left < 0) == (right < 0) else -q
        if kind == "if":
            _, op, le, re, th, el = node
            left = ev(le)
            if isinstance(left, str):
                return left
            right = ev(re)
            if isinstance(right, str):
                return right
            ok = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }[op]
            return ev(th if ok else el)
        # function call
        _, name, args = node
        vals = []
        for a in args:
            if a[0] == "range":
                for nm in _range_cells(a[1], a[2]):
                    if nm not in cells:
                        continue
                    v = ref(nm)
                    if isinstance(v, str):
                        return v
                    vals.append(v)
            else:
                v = ev(a[1])
                if isinstance(v, str):
                    return v
                vals.append(v)
        if name == "SUM":
            return sum(vals)
        if name == "MIN":
            return min(vals) if vals else 0
        return max(vals) if vals else 0

    return {name: ref(name) for name in cells}


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 1000000))
    threading.stack_size(256 * 1024 * 1024)
    box = {}

    def run():
        try:
            box["result"] = _solve(cells)
        except BaseException as exc:
            box["error"] = exc

    t = threading.Thread(target=run)
    t.start()
    t.join()
    if "error" in box:
        raise box["error"]
    return box["result"]
