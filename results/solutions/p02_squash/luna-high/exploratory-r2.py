def squash(s: str) -> str:
    parts = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        c = s[i]
        escaped = "\\" + c if c == "\\" or "0" <= c <= "9" else c
        run_length = j - i

        if run_length >= 3:
            parts.append(str(run_length))
            parts.append(escaped)
        else:
            parts.append(escaped * run_length)

        i = j

    return "".join(parts)
