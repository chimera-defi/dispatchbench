def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    mask = (1 << n) - 1
    value = sum((ch == "1") << i for i, ch in enumerate(state))
    shifts = [offset % n for offset in offsets]

    while t:
        if t & 1:
            result = 0
            for shift in shifts:
                if shift:
                    rotated = (value >> shift) | (value << (n - shift))
                    result ^= rotated & mask
                else:
                    result ^= value
            value = result

        shifts = [(shift * 2) % n for shift in shifts]
        t >>= 1

    return "".join("1" if (value >> i) & 1 else "0" for i in range(n))
