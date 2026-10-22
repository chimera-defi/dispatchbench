def squash(s: str) -> str:
    parts = []
    i = 0
    n = len(s)

    while i < n:
        c = s[i]
        j = i + 1
        while j < n and s[j] == c:
            j += 1

        length = j - i
        escaped = "\\" + c if "0" <= c <= "9" or c == "\\" else c
        if length >= 3:
            parts.append(str(length))
            parts.append(escaped)
        else:
            parts.append(escaped * length)

        i = j

    return "".join(parts)
