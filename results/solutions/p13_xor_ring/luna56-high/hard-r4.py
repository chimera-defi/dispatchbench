def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def carryless_mul(a: int, b: int) -> int:
        if not a or not b:
            return 0

        if a.bit_length() < b.bit_length():
            a, b = b, a

        if b.bit_count() <= 32:
            result = 0
            while b:
                bit = b & -b
                result ^= a << (bit.bit_length() - 1)
                b ^= bit
            return result

        if min(a.bit_length(), b.bit_length()) <= 128:
            result = 0
            while b:
                if b & 1:
                    result ^= a
                a <<= 1
                b >>= 1
            return result

        m = max(a.bit_length(), b.bit_length()) // 2
        low_mask = (1 << m) - 1

        a0, a1 = a & low_mask, a >> m
        b0, b1 = b & low_mask, b >> m

        z0 = carryless_mul(a0, b0)
        z2 = carryless_mul(a1, b1)
        z1 = carryless_mul(a0 ^ a1, b0 ^ b1) ^ z0 ^ z2

        return z0 ^ (z1 << m) ^ (z2 << (2 * m))

    def cyclic_mul(a: int, b: int) -> int:
        product = carryless_mul(a, b)
        return (product & mask) ^ (product >> n)

    current = sum((bit << i) for i, bit in enumerate(state) if bit == "1")

    kernel = 0
    for offset in offsets:
        kernel ^= 1 << ((-offset) % n)

    result = 1
    power = kernel

    while t:
        if t & 1:
            result = cyclic_mul(result, power)
        t >>= 1
        if t:
            power = cyclic_mul(power, power)

    answer = cyclic_mul(result, current)
    return format(answer, f"0{n}b")[::-1]
