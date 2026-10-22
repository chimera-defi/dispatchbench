def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    out = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        count = j - i
        if count >= 3:
            out.append(str(count))
            out.append(esc(s[i]))
        else:
            out.extend([esc(s[i])] * count)

        i = j

    return "".join(out)
