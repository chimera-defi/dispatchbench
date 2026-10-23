def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    value = 0
    for i, ch in enumerate(state):
        if ch == "1":
            value |= 1 << i

    kernel = 0
    for offset in offsets:
        pos = offset % n
        kernel ^= 1 << pos

    def rotate_right(x: int, shift: int) -> int:
        if shift == 0:
            return x
        return ((x >> shift) | (x << (n - shift))) & mask

    def apply(x: int, k: int) -> int:
        result = 0
        while k:
            bit = k & -k
            shift = bit.bit_length() - 1
            result ^= rotate_right(x, shift)
            k ^= bit
        return result

    while t:
        if t & 1:
            value = apply(value, kernel)

        squared = 0
        k = kernel
        while k:
            bit = k & -k
            pos = bit.bit_length() - 1
            squared ^= 1 << ((2 * pos) % n)
            k ^= bit

        kernel = squared
        t >>= 1

    return format(value, f"0{n}b")[::-1]
