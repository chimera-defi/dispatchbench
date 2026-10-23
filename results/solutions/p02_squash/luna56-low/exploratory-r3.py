def squash(s: str) -> str:
    if not s:
        return ""

    out = []
    start = 0
    n = len(s)

    while start < n:
        end = start + 1
        while end < n and s[end] == s[start]:
            end += 1

        length = end - start
        char = s[start]
        escaped = "\\" + char if char.isdigit() or char == "\\" else char

        if length >= 3:
            out.append(str(length))
            out.append(escaped)
        else:
            out.append(escaped * length)

        start = end

    return "".join(out)
