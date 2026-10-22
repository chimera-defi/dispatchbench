def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1

    def multiply(a: int, b: int) -> int:
        # Cyclic convolution over GF(2).
        if a.bit_count() > b.bit_count():
            a, b = b, a

        result = 0
        while a:
            bit = a & -a
            shift = bit.bit_length() - 1
            if shift == 0:
                result ^= b
            else:
                result ^= ((b << shift) | (b >> (n - shift))) & mask
            a ^= bit
        return result

    # Encode offset d as exponent -d so the result at i uses state[i + d].
    base = 0
    for offset in offsets:
        base ^= 1 << ((-offset) % n)

    power = 1  # Multiplicative identity.
    while t:
        if t & 1:
            power = multiply(power, base)

        # Squaring over GF(2) doubles every exponent.
        squared = 0
        bits = base
        while bits:
            bit = bits & -bits
            index = bit.bit_length() - 1
            squared ^= 1 << ((2 * index) % n)
            bits ^= bit
        base = squared
        t >>= 1

    initial = sum((1 << i) for i, value in enumerate(state) if value == "1")
    result = multiply(power, initial)

    return "".join("1" if (result >> i) & 1 else "0" for i in range(n))
