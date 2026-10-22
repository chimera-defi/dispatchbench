def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    s = 0
    for i, c in enumerate(state):
        if c == '1':
            s |= 1 << i

    p = 0
    for d in offsets:
        p ^= 1 << ((-d) % n)

    def mul(a, b):
        if bin(a).count('1') > bin(b).count('1'):
            a, b = b, a
        res = 0
        while a:
            low = a & -a
            k = low.bit_length() - 1
            a ^= low
            if k == 0:
                res ^= b
            else:
                res ^= ((b << k) | (b >> (n - k))) & mask
        return res

    result = s
    base = p
    e = t
    while e:
        if e & 1:
            result = mul(base, result)
        e >>= 1
        if e:
            base = mul(base, base)

    return format(result, 'b').zfill(n)[::-1]
