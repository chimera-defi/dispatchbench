def squash(s: str) -> str:
    out = []
    n = len(s)
    i = 0
    while i < n:
        c = s[i]
        j = i
        while j < n and s[j] == c:
            j += 1
        k = j - i
        e = "\\" + c if (c.isdigit() and c in "0123456789") or c == "\\" else c
        if k >= 3:
            out.append(str(k))
            out.append(e)
        else:
            out.append(e * k)
        i = j
    return "".join(out)
