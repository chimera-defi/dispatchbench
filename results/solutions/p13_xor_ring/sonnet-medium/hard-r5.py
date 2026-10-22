def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def mul(a, b):
        r = 0
        while a:
            low = a & -a
            r ^= b << (low.bit_length() - 1)
            a ^= low
        return (r & mask) ^ (r >> n)

    s = 0
    for j, ch in enumerate(state):
        if ch == '1':
            s |= 1 << j

    q = 0
    for d in offsets:
        q ^= 1 << ((-d) % n)

    while t:
        if t & 1:
            s = mul(s, q)
        t >>= 1
        if t:
            q = mul(q, q)

    return ''.join('1' if (s >> j) & 1 else '0' for j in range(n))
