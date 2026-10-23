def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    values = [c == "1" for c in state]

    current = []
    for offset in offsets:
        d = offset % n
        if d in current:
            current.remove(d)
        else:
            current.append(d)

    while t:
        if t & 1:
            values = [
                sum(values[(i + d) % n] for d in current) & 1
                for i in range(n)
            ]

        t >>= 1
        if t:
            doubled = []
            for d in current:
                nd = (2 * d) % n
                if nd in doubled:
                    doubled.remove(nd)
                else:
                    doubled.append(nd)
            current = doubled

    return "".join("1" if value else "0" for value in values)
