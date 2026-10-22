def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c == "\\" or "0" <= c <= "9" else c

    parts = []
    i = 0
    while i < len(s):
        j = i + 1
        while j < len(s) and s[j] == s[i]:
            j += 1

        count = j - i
        if count >= 3:
            parts.append(str(count) + esc(s[i]))
        else:
            parts.append(esc(s[i]) * count)

        i = j

    return "".join(parts)
