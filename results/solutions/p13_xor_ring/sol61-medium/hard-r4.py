def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    bits = int(state, 2)

    shifts = set()
    for offset in offsets:
        d = offset % n
        shifts.symmetric_difference_update({d})

    while t:
        if not shifts:
            return "0" * n

        if t & 1:
            result = 0
            for d in shifts:
                result ^= ((bits << d) & mask) | (bits >> (n - d))
            bits = result

        t >>= 1
        if t:
            next_shifts = set()
            for d in shifts:
                next_shifts.symmetric_difference_update({(2 * d) % n})
            shifts = next_shifts

    return format(bits, f"0{n}b")
