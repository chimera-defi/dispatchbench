def squash(s: str) -> str:
    parts = []
    n = len(s)
    i = 0

    while i < n:
        c = s[i]
        j = i + 1
        while j < n and s[j] == c:
            j += 1

        count = j - i
        escaped = "\\" + c if "0" <= c <= "9" or c == "\\" else c

        if count >= 3:
            parts.append(str(count))
            parts.append(escaped)
        else:
            parts.append(escaped * count)

        i = j

    return "".join(parts)
