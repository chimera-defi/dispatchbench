def squash(s: str) -> str:
    def esc(c: str) -> str:
        if c in "0123456789\\":
            return "\\" + c
        return c

    out = []
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
