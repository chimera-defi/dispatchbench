def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def rot(a: int, k: int) -> int:
        # Cyclic left shift of an n-bit polynomial by k positions.
        return ((a << k) | (a >> (n - k))) & mask

    def mul(a: int, b: int) -> int:
        # Multiplication in GF(2)[x] / (x^n - 1).
        res = 0
        while b:
            low = b & -b
            res ^= rot(a, low.bit_length() - 1)
            b ^= low
        return res

    # Q(x) = sum of x^(-d) over offsets; cancelling pairs drop out via XOR.
    q = 0
    for d in offsets:
        q ^= 1 << ((-d) % n)

    # Lamp state as a polynomial: bit i holds lamp i.
    s = 0
    for i, c in enumerate(state):
        if c == '1':
            s |= 1 << i

    # Compute s * Q^t by fast exponentiation.
    result = s
    base = q
    e = t
    while e:
        if e & 1:
            result = mul(result, base)
        e >>= 1
        if e:
            base = mul(base, base)

    return ''.join('1' if (result >> i) & 1 else '0' for i in range(n))
