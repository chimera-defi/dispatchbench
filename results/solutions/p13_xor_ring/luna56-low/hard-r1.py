def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)

    if t == 0:
        return state

    base = set()
    for d in offsets:
        d %= n
        if d in base:
            base.remove(d)
        else:
            base.add(d)

    if not base:
        return "0" * n

    current = bytearray(1 if c == "1" else 0 for c in state)

    k = 0
    while t:
        if t & 1:
            transformed = bytearray(n)
            for d in base:
                for i in range(n):
                    j = i + d
                    if j >= n:
                        j -= n
                    transformed[i] ^= current[j]
            current = transformed

        base = {(d * 2) % n for d in base}
        t >>= 1

    return "".join("1" if x else "0" for x in current)
