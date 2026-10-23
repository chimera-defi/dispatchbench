def squash(s: str) -> str:
    result = []
    n = len(s)
    i = 0

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        run_length = j - i
        c = s[i]
        escaped = "\\" + c if c.isdigit() or c == "\\" else c

        if run_length >= 3:
            result.append(str(run_length))
            result.append(escaped)
        else:
            result.append(escaped * run_length)

        i = j

    return "".join(result)
