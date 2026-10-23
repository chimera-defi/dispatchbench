def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    value = int(state, 2)
    shifts = [d % n for d in offsets]

    while t:
        if t & 1:
            next_value = 0
            for d in shifts:
                # Left rotation makes lamp i copy lamp (i + d) % n.
                next_value ^= ((value << d) & mask) | (value >> (n - d))
            value = next_value

        # Over XOR, squaring the update doubles every offset:
        # all cross terms occur twice and cancel.
        shifts = [(2 * d) % n for d in shifts]
        t >>= 1

    return format(value, f"0{n}b")
