def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    # Bit i represents lamp i or offset i.
    values = int(state[::-1], 2)

    kernel = 0
    for offset in offsets:
        kernel ^= 1 << (offset % n)

    def apply(x: int, k: int) -> int:
        result = 0
        while k:
            bit = k & -k
            shift = bit.bit_length() - 1
            if shift == 0:
                rotated = x
            else:
                rotated = (x >> shift) | ((x << (n - shift)) & mask)
            result ^= rotated
            k ^= bit
        return result

    while t:
        if t & 1:
            values = apply(values, kernel)
        t >>= 1
        if t:
            squared = 0
            bits = kernel
            while bits:
                bit = bits & -bits
                shift = bit.bit_length() - 1
                squared ^= 1 << ((2 * shift) % n)
                bits ^= bit
            kernel = squared

    return format(values, f"0{n}b")[::-1]
