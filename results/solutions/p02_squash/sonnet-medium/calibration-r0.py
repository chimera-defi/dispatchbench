def squash(s: str) -> str:
    def esc(c):
        return "\\" + c if c.isdigit() and c in "0123456789" or c == "\\" else c

    out = []
    n = len(s)
    i = 0
    while i < n:
        c = s[i]
        j = i
        while j < n and s[j] == c:
            j += 1
        run = j - i
        e = esc(c)
        if run >= 3:
            out.append(str(run))
            out.append(e)
        else:
            out.append(e * run)
        i = j
    return "".join(out)
