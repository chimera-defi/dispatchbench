def squash(s: str) -> str:
    if not s:
        return ""

    parts = []
    start = 0

    for i in range(1, len(s) + 1):
        if i == len(s) or s[i] != s[start]:
            char = s[start]
            escaped = "\\" + char if char.isdigit() or char == "\\" else char
            length = i - start

            if length >= 3:
                parts.append(str(length))
                parts.append(escaped)
            else:
                parts.append(escaped * length)

            start = i

    return "".join(parts)
