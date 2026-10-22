def squash(s: str) -> str:
    out = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        char = s[i]
        escaped = "\\" + char if char.isdigit() or char == "\\" else char
        length = j - i

        if length >= 3:
            out.append(str(length))
            out.append(escaped)
        else:
            out.append(escaped * length)

        i = j

    return "".join(out)
