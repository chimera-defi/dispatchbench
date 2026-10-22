def squash(s: str) -> str:
    out = []
    n = len(s)
    i = 0

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        count = j - i
        c = s[i]
        escaped = "\\" + c if c.isdigit() or c == "\\" else c

        if count >= 3:
            out.append(str(count))
            out.append(escaped)
        else:
            out.append(escaped * count)

        i = j

    return "".join(out)
