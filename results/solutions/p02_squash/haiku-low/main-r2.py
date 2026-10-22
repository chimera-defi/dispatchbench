def squash(s: str) -> str:
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        j = i
        while j < n and s[j] == c:
            j += 1
        run = j - i
        esc = ('\\' + c) if c in "0123456789\\" else c
        if run >= 3:
            out.append(str(run) + esc)
        else:
            out.append(esc * run)
        i = j
    return "".join(out)
