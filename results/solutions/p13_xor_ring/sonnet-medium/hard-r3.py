def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1
    s = int(state[::-1], 2)
    k = 0
    while t >> k:
        if (t >> k) & 1:
            m = pow(2, k, n)
            res = 0
            for d in offsets:
                r = (d % n) * m % n
                if r == 0:
                    res ^= s
                else:
                    res ^= (s >> r) | ((s << (n - r)) & mask)
            s = res
        k += 1
    return format(s, '0{}b'.format(n))[::-1]
