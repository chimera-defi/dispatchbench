def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)

    counts = {}
    for offset in offsets:
        r = offset % n
        counts[r] = counts.get(r, 0) ^ 1

    active = [r for r, bit in counts.items() if bit]
    if not active:
        return "0" * n

    def multiply(a, b):
        result = [0] * (2 * n - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        result[i + j] ^= 1

        for degree in range(2 * n - 2, n - 1, -1):
            if result[degree]:
                result[degree] = 0
                for r in active:
                    result[degree - n + r] ^= 1

        return result[:n]

    base = [0] * n
    for r in active:
        base[r] = 1

    power = [0] * n
    power[0] = 1

    while t:
        if t & 1:
            power = multiply(power, base)
        base = multiply(base, base)
        t >>= 1

    initial = [c == "1" for c in state]
    result = [False] * n

    for shift, bit in enumerate(power):
        if bit:
            for i, value in enumerate(initial):
                if value:
                    result[(i - shift) % n] ^= True

    return "".join("1" if value else "0" for value in result)
