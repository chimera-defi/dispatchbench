def squash(s: str) -> str:
    result = []
    i = 0
    n = len(s)

    while i < n:
        c = s[i]
        j = i + 1
        while j < n and s[j] == c:
            j += 1

        count = j - i
        escaped = "\\" + c if "0" <= c <= "9" or c == "\\" else c

        if count >= 3:
            result.append(str(count))
            result.append(escaped)
        else:
            result.append(escaped * count)

        i = j

    return "".join(result)
