def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    result = []
    i = 0
    while i < len(s):
        j = i + 1
        while j < len(s) and s[j] == s[i]:
            j += 1

        count = j - i
        if count >= 3:
            result.append(str(count))
            result.append(esc(s[i]))
        else:
            result.extend([esc(s[i])] * count)
        i = j

    return "".join(result)
