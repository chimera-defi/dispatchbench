def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)

    if t == 0:
        return state

    counts = {}
    for offset in offsets:
        k = offset % n
        counts[k] = counts.get(k, 0) ^ 1

    shifts = [k for k, parity in counts.items() if parity]
    if not shifts:
        return "0" * n

    current = bytearray(c == "1" for c in state)
    bit = 0

    while t:
        if t & 1:
            factor_shifts = [(shift * (1 << bit)) % n for shift in shifts]
            nxt = bytearray(n)

            for i in range(n):
                value = 0
                for shift in factor_shifts:
                    value ^= current[(i + shift) % n]
                nxt[i] = value

            current = nxt

        t >>= 1
        bit += 1

    return "".join("1" if value else "0" for value in current)
