def squash(s: str) -> str:
    out = []
    n = len(s)
    i = 0

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        char = s[i]
        count = j - i
        escaped = "\\" + char if char.isdigit() or char == "\\" else char

        if count >= 3:
            out.append(str(count))
            out.append(escaped)
        else:
            out.append(escaped * count)

        i = j

    return "".join(out)
