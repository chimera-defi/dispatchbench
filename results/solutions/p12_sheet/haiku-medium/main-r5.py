import operator
import re
import sys
import threading

_DIV0 = "#DIV/0!"
_CYCLE = "#CYCLE!"
_TOKEN_RE = re.compile(r"([A-Z][1-9][0-9]*)|([A-Z]+)|([0-9]+)|(<>|<=|>=|[-+*/()=<>,:])")
_CMP = {
    "=": operator.eq,
    "<>": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


def _tokenize(text):
    text = re.sub(r"\s+", "", text)
    tokens = []
    pos = 0
    while pos < len(text):
        m = _TOKEN_RE.match(text, pos)
        if m is None:
            raise ValueError("bad formula: " + text)
        if m.group(1):
            tokens.append(("cell", m.group(1)))
        elif m.group(2):
            tokens.append(("word", m.group(2)))
        elif m.group(3):
            tokens.append(("num", int(m.group(3))))
        else:
            tokens.append(("op", m.group(4)))
        pos = m.end()
    return tokens


def _range_cells(c1, c2):
    col1, row1 = ord(c1[0]), int(c1[1:])
    col2, row2 = ord(c2[0]), int(c2[1:])
    for r in range(min(row1, row2), max(row1, row2) + 1):
        for c in range(min(col1, col2), max(col1, col2) + 1):
            yield f"{chr(c)}{r}"


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    values = {}
    in_progress = set()

    def parse(text):
        toks = _tokenize(text)
        pos = [0]

        def peek():
            return toks[pos[0]] if pos[0] < len(toks) else None

        def take():
            t = toks[pos[0]]
            pos[0] += 1
            return t

        def is_op(t, s):
            return t is not None and t[0] == "op" and t[1] == s

        def expect(s):
            if not is_op(take(), s):
                raise ValueError("expected " + s)

        def formula():
            node = term()
            while is_op(peek(), "+") or is_op(peek(), "-"):
                op = take()[1]
                node = ("bin", op, node, term())
            return node

        def term():
            node = unary()
            while is_op(peek(), "*") or is_op(peek(), "/"):
                op = take()[1]
                node = ("bin", op, node, unary())
            return node

        def unary():
            if is_op(peek(), "-"):
                take()
                return ("neg", unary())
            return atom()

        def arg():
            save = pos[0]
            if peek() is not None and peek()[0] == "cell":
                c1 = take()[1]
                if is_op(peek(), ":"):
                    take()
                    c2 = take()[1]
                    return ("range", c1, c2)
                pos[0] = save
            return formula()

        def atom():
            t = take()
            if t[0] == "num":
                return ("num", t[1])
            if t[0] == "cell":
                return ("ref", t[1])
            if is_op(t, "("):
                node = formula()
                expect(")")
                return node
            name = t[1]
            expect("(")
            if name == "IF":
                left = formula()
                op = take()[1]
                right = formula()
                expect(",")
                then = formula()
                expect(",")
                other = formula()
                expect(")")
                return ("if", op, left, right, then, other)
            args = [arg()]
            while is_op(peek(), ","):
                take()
                args.append(arg())
            expect(")")
            return ("call", name, args)

        node = formula()
        if pos[0] != len(toks):
            raise ValueError("trailing tokens")
        return node

    def ref(name):
        if name not in cells:
            return 0
        if name in values:
            return values[name]
        if name in in_progress:
            return _CYCLE
        in_progress.add(name)
        content = cells[name]
        if content.startswith("="):
            v = ev(parse(content[1:]))
        else:
            v = int(content.strip())
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
            left = ev(node[2])
            if isinstance(left, str):
                return left
            right = ev(node[3])
            if isinstance(right, str):
                return right
            chosen = node[4] if _CMP[node[1]](left, right) else node[5]
            return ev(chosen)
        # function call
        name, args = node[1], node[2]
        vals = []
        for a in args:
            if a[0] == "range":
                for cname in _range_cells(a[1], a[2]):
                    if cname in cells:
                        v = ref(cname)
                        if isinstance(v, str):
                            return v
                        vals.append(v)
            else:
                v = ev(a)
                if isinstance(v, str):
                    return v
                vals.append(v)
        if name == "SUM":
            return sum(vals)
        if not vals:
            return 0
        return min(vals) if name == "MIN" else max(vals)

    def solve():
        try:
            for name in cells:
                ref(name)
        except BaseException as exc:  # re-raised in caller
            errors.append(exc)

    errors = []
    old_limit = sys.getrecursionlimit()
    old_stack = threading.stack_size()
    sys.setrecursionlimit(max(old_limit, 100000))
    try:
        threading.stack_size(256 * 1024 * 1024)
        worker = threading.Thread(target=solve)
        worker.start()
        worker.join()
    finally:
        threading.stack_size(old_stack)
        sys.setrecursionlimit(old_limit)
    if errors:
        raise errors[0]
    return {name: values[name] for name in cells}
