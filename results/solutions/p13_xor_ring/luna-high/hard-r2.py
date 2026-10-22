def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    value = sum((ch == "1") << i for i, ch in enumerate(state))

    # Encode each offset as the corresponding left shift of the state.
    kernel = 0
    for offset in offsets:
        kernel ^= 1 << ((-offset) % n)

    def apply(x: int, shifts: int) -> int:
        result = 0
        while shifts:
            bit = shifts & -shifts
            shift = bit.bit_length() - 1
            if shift == 0:
                result ^= x
            else:
                result ^= ((x << shift) | (x >> (n - shift))) & mask
            shifts ^= bit
        return result

    while t:
        if t & 1:
            value = apply(value, kernel)

        t >>= 1
        if t:
            squared = 0
            bits = kernel
            while bits:
                bit = bits & -bits
                index = bit.bit_length() - 1
                squared ^= 1 << ((2 * index) % n)
                bits ^= bit
            kernel = squared

    return "".join("1" if (value >> i) & 1 else "0" for i in range(n))
