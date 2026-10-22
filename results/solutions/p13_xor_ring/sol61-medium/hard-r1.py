def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    value = int(state, 2)
    shifts = [d % n for d in offsets]

    # Over XOR, raising the update operator to 2**k simply
    # multiplies each offset by 2**k.
    while t:
        if t & 1:
            result = 0
            for d in shifts:
                result ^= ((value << d) & mask) | (value >> (n - d))
            value = result

        t >>= 1
        if t:
            shifts = [(2 * d) % n for d in shifts]

    return format(value, f"0{n}b")
