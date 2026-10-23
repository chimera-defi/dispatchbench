def squash(s: str) -> str:
    result = []
    i = 0

    while i < len(s):
        j = i + 1
        while j < len(s) and s[j] == s[i]:
            j += 1

        count = j - i
        char = s[i]
        escaped = "\\" + char if char.isdigit() or char == "\\" else char

        if count >= 3:
            result.append(str(count))
            result.append(escaped)
        else:
            result.append(escaped * count)

        i = j

    return "".join(result)
