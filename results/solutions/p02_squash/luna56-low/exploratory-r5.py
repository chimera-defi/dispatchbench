def squash(s: str) -> str:
    if not s:
        return ""

    parts = []
    n = len(s)
    i = 0

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        count = j - i
        char = s[i]
        escaped = "\\" + char if char.isdigit() or char == "\\" else char

        if count >= 3:
            parts.append(str(count))
            parts.append(escaped)
        else:
            parts.append(escaped * count)

        i = j

    return "".join(parts)
