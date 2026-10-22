def squash(s: str) -> str:
    out = []

    def esc(c: str) -> str:
        if c.isdigit() or c == "\\":
            return "\\" + c
        return c

    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        j = i
        while j < n and s[j] == c:
            j += 1
        run = j - i
        if run >= 3:
            out.append(str(run) + esc(c))
        else:
            out.append(esc(c) * run)
        i = j
    return "".join(out)
