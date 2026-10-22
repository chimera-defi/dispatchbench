def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def mul(a, b):
        res = 0
        while a:
            low = a & -a
            res ^= b << (low.bit_length() - 1)
            a ^= low
        res = (res & mask) ^ (res >> n)
        return (res & mask) ^ (res >> n)

    k = 0
    for d in offsets:
        k ^= 1 << ((-d) % n)

    s = 0
    for i, c in enumerate(state):
        if c == '1':
            s |= 1 << i

    while t:
        if t & 1:
            s = mul(s, k)
        t >>= 1
        if t:
            k = mul(k, k)

    return ''.join('1' if (s >> i) & 1 else '0' for i in range(n))
