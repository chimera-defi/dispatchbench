from itertools import groupby


def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    out = []
    for c, group in groupby(s):
        n = sum(1 for _ in group)
        if n >= 3:
            out.append(str(n) + esc(c))
        else:
            out.append(esc(c) * n)
    return "".join(out)
