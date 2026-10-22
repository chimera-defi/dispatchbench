import re
import sys

_DIV0 = "#DIV/0!"
_CYCLE = "#CYCLE!"
_FUNCS = ("SUM", "MIN", "MAX")
_TOKEN_RE = re.compile(r"<>|<=|>=|[A-Z]+\d*|\d+|[-+*/(),:=<>]")
_CELL_RE = re.compile(r"[A-Z]\d+")


def _parse(src):
    tokens = _TOKEN_RE.findall(src)
    pos = 0

    def peek(k=0):
        return tokens[pos + k] if pos + k < len(tokens) else None

    def take():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def expr():
        node = term()
        while peek() in ("+", "-"):
            op = take()
            node = ("bin", op, node, term())
        return node

    def term():
        node = unary()
        while peek() in ("*", "/"):
            op = take()
            node = ("bin", op, node, unary())
        return node

    def unary():
        if peek() == "-":
            take()
            return ("neg", unary())
        return atom()

    def arg():
        if peek(1) == ":":
            a = take()
            take()
            b = take()
            return ("range", a, b)
        return expr()

    def atom():
        tok = take()
        if tok == "(":
            node = expr()
            take()
            return node
        if tok.isdigit():
            return ("num", int(tok))
        if _CELL_RE.fullmatch(tok):
            return ("ref", tok)
        if tok == "IF":
            take()
            left = expr()
            op = take()
            right = expr()
            take()
            then = expr()
            take()
            other = expr()
            take()
            return ("if", op, left, right, then, other)
        if tok in _FUNCS:
            take()
            args = [arg()]
            while peek() == ",":
                take()
                args.append(arg())
            take()
            return ("call", tok, args)
        raise ValueError("unexpected token: " + tok)

    return expr()


def sheet(cells: dict[str, str]) -> dict[str, int | str]:
    if sys.getrecursionlimit() < 100000:
        sys.setrecursionlimit(100000)

    results = {}
    busy = set()

    def cell_value(name):
        if name not in cells:
            return 0
        if name in results:
            return results[name]
        if name in busy:
            return _CYCLE
        content = cells[name].strip()
        if not content.startswith("="):
            results[name] = int(content)
            return results[name]
        busy.add(name)
        value = ev(_parse(content[1:]))
        busy.discard(name)
        results[name] = value
        return value

    def range_names(a, b):
        r1, r2 = sorted((int(a[1:]), int(b[1:])))
        c1, c2 = sorted((ord(a[0]), ord(b[0])))
        for row in range(r1, r2 + 1):
            for col in range(c1, c2 + 1):
                yield chr(col) + str(row)

    def ev(node):
        kind = node[0]
        if kind == "num":
            return node[1]
        if kind == "ref":
            return cell_value(node[1])
        if kind == "neg":
            v = ev(node[1])
            return v if isinstance(v, str) else -v
        if kind == "bin":
            op = node[1]
            left = ev(node[2])
            if isinstance(left, str):
                return left
            right = ev(node[3])
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
            quotient = abs(left) // abs(right)
            return quotient if (left < 0) == (right < 0) else -quotient
        if kind == "call":
            fname, args = node[1], node[2]
            vals = []
            for a in args:
                if a[0] == "range":
                    for name in range_names(a[1], a[2]):
                        if name not in cells:
                            continue
                        v = cell_value(name)
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
            if fname == "SUM":
                return sum(vals)
            if fname == "MIN":
                return min(vals)
            return max(vals)
        if kind == "if":
            op = node[1]
            left = ev(node[2])
            if isinstance(left, str):
                return left
            right = ev(node[3])
            if isinstance(right, str):
                return right
            conds = {
                "=": left == right,
                "<>": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
            }
            return ev(node[4]) if conds[op] else ev(node[5])
        raise ValueError("unknown node: " + kind)

    return {name: cell_value(name) for name in cells}
