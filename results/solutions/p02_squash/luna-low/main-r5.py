def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    parts = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        count = j - i
        if count >= 3:
            parts.append(str(count))
            parts.append(esc(s[i]))
        else:
            parts.extend([esc(s[i])] * count)

        i = j

    return "".join(parts)
