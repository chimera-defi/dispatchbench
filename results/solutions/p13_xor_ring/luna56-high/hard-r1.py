def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    vector = 0
    for i, ch in enumerate(state):
        if ch == "1":
            vector |= 1 << i

    kernel = 0
    for offset in offsets:
        kernel ^= 1 << ((-offset) % n)

    def multiply(a: int, b: int) -> int:
        if a.bit_count() > b.bit_count():
            a, b = b, a

        result = 0
        while a:
            bit = a & -a
            i = bit.bit_length() - 1
            if i == 0:
                result ^= b
            else:
                result ^= ((b << i) | (b >> (n - i))) & mask
            a ^= bit
        return result & mask

    def square(a: int) -> int:
        result = 0
        while a:
            bit = a & -a
            i = bit.bit_length() - 1
            result ^= 1 << ((2 * i) % n)
            a ^= bit
        return result & mask

    result = 1
    while t:
        if t & 1:
            result = multiply(result, kernel)
        kernel = square(kernel)
        t >>= 1

    vector = multiply(result, vector)
    return "".join("1" if (vector >> i) & 1 else "0" for i in range(n))
