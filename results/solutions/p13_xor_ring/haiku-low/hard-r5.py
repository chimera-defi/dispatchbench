def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    # Each offset d contributes x^(-d mod n) to the characteristic polynomial.
    # Terms appearing an even number of times cancel over GF(2).
    parity = {}
    for d in offsets:
        e = (-d) % n
        parity[e] = parity.get(e, 0) ^ 1
    p = 0
    for e, bit in parity.items():
        if bit:
            p |= 1 << e

    def rot(a, i):
        # Multiply a by x^i modulo x^n - 1.
        i %= n
        if i == 0:
            return a
        return ((a << i) | (a >> (n - i))) & mask

    def mul(a, b):
        # Cyclic polynomial product over GF(2), reduced mod x^n - 1.
        res = 0
        while b:
            low = b & -b
            res ^= rot(a, low.bit_length() - 1)
            b ^= low
        return res

    # Lamp i is bit i of v.
    v = 0
    for i, ch in enumerate(state):
        if ch == '1':
            v |= 1 << i

    # v * P^t by binary exponentiation.
    base = p
    while t:
        if t & 1:
            v = mul(v, base)
        t >>= 1
        if t:
            base = mul(base, base)

    return ''.join('1' if (v >> i) & 1 else '0' for i in range(n))
