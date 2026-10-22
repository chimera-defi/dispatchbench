def squash(s: str) -> str:
    if not s:
        return ""

    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    result = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        count = j - i
        encoded = esc(s[i])
        if count >= 3:
            result.append(str(count))
            result.append(encoded)
        else:
            result.extend([encoded] * count)

        i = j

    return "".join(result)
