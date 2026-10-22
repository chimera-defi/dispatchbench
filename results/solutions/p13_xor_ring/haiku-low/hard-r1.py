def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def mul(a: int, b: int) -> int:
        # Carry-less product of polynomials over GF(2), reduced mod x^n - 1.
        r = 0
        while a:
            low = a & -a
            r ^= b << (low.bit_length() - 1)
            a ^= low
        # Fold degrees >= n back down (x^n == 1).
        return (r & mask) ^ (r >> n)

    # Operator polynomial: new[i] = XOR_k c_k * old[(i + k) mod n],
    # realised as convolution with q_j = c_{(-j) mod n}.
    q = 0
    for d in offsets:
        j = (-d) % n
        q ^= 1 << j

    # State polynomial: bit i holds lamp i.
    s = 0
    for i, ch in enumerate(state):
        if ch == '1':
            s |= 1 << i

    # Compute q^t by binary exponentiation.
    result = 1
    base = q
    e = t
    while e:
        if e & 1:
            result = mul(result, base)
        e >>= 1
        if e:
            base = mul(base, base)

    final = mul(result, s)
    return ''.join('1' if (final >> i) & 1 else '0' for i in range(n))
