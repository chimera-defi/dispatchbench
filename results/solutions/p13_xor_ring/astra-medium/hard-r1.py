def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    value = int(state, 2)

    shifts = set()
    for offset in offsets:
        d = offset % n
        shifts.symmetric_difference_update((d,))

    while t and shifts and value:
        if t & 1:
            result = 0
            for d in shifts:
                result ^= ((value << d) & mask) | (value >> (n - d))
            value = result

        t >>= 1
        if t:
            doubled = set()
            for d in shifts:
                doubled.symmetric_difference_update(((2 * d) % n,))
            shifts = doubled

    if t and not shifts:
        value = 0

    return format(value, f"0{n}b")
