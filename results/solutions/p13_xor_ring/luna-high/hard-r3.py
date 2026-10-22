def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    if t == 0:
        return state

    mask = (1 << n) - 1

    def multiply(a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
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
        return result

    power = 0
    for d in offsets:
        power ^= 1 << ((-d) % n)

    result = 1
    while t:
        if t & 1:
            result = multiply(result, power)
        t >>= 1
        if t:
            squared = 0
            bits = power
            while bits:
                bit = bits & -bits
                i = bit.bit_length() - 1
                squared ^= 1 << ((2 * i) % n)
                bits ^= bit
            power = squared

    lamps = 0
    for i, value in enumerate(state):
        if value == "1":
            lamps |= 1 << i

    lamps = multiply(lamps, result)
    return "".join("1" if (lamps >> i) & 1 else "0" for i in range(n))
