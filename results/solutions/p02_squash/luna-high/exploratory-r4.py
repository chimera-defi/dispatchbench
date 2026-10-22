def squash(s: str) -> str:
    result = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        char = s[i]
        escaped = "\\" + char if char.isdigit() or char == "\\" else char
        count = j - i

        if count >= 3:
            result.append(str(count))
            result.append(escaped)
        else:
            result.append(escaped * count)

        i = j

    return "".join(result)
