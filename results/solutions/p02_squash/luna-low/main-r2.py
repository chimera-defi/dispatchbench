def squash(s: str) -> str:
    out = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        c = s[i]
        count = j - i
        escaped = "\\" + c if c.isdigit() or c == "\\" else c

        if count >= 3:
            out.append(str(count))
            out.append(escaped)
        else:
            out.extend([escaped] * count)

        i = j

    return "".join(out)
