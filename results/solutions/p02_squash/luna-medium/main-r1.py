def squash(s: str) -> str:
    def esc(c: str) -> str:
        return "\\" + c if c.isdigit() or c == "\\" else c

    out = []
    i = 0
    n = len(s)

    while i < n:
        j = i + 1
        while j < n and s[j] == s[i]:
            j += 1

        run_length = j - i
        if run_length >= 3:
            out.append(str(run_length))
            out.append(esc(s[i]))
        else:
            out.extend([esc(s[i])] * run_length

)
        i = j

    return "".join(out)
