def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1
    s = int(state[::-1], 2)
    k = 0
    while t >> k:
        if (t >> k) & 1:
            p = pow(2, k, n)
            new = 0
            for d in offsets:
                r = (d * p) % n
                new ^= ((s >> r) | (s << (n - r))) & mask
            s = new
        k += 1
    return format(s, '0%db' % n)[::-1]
