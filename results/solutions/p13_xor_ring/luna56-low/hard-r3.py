def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def multiply(a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        if a.bit_count() > b.bit_count():
            a, b = b, a

        result = 0
        x = a
        while x:
            bit = x & -x
            shift = bit.bit_length() - 1
            result ^= ((b << shift) | (b >> (n - shift))) & mask
            x ^= bit
        return result

    current = 0
    for i, ch in enumerate(state):
        if ch == "1":
            current |= 1 << i

    if t == 0:
        return state

    operator = 0
    for offset in offsets:
        operator ^= 1 << ((-offset) % n)

    while t:
        if t & 1:
            current = multiply(current, operator)
        t >>= 1
        if t:
            operator = multiply(operator, operator)

    return "".join("1" if (current >> i) & 1 else "0" for i in range(n))
