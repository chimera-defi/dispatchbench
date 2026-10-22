def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    out = []
    i = 0
    while i < len(s):
        j = i + 1
        while j < len(s) and s[j] == s[i]:
            j += 1

        count = j - i
        encoded = esc(s[i])
        if count >= 3:
            out.append(str(count))
            out.append(encoded)
        else:
            out.append(encoded * count)

        i = j

    return "".join(out)
