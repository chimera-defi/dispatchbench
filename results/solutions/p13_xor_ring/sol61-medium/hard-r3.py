def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    value = int(state, 2)

    shifts = set()
    for offset in offsets:
        shift = offset % n
        shifts.symmetric_difference_update((shift,))

    while t:
        if not shifts or value == 0:
            return "0" * n

        if t & 1:
            result = 0
            for shift in shifts:
                result ^= ((value << shift) & mask) | (value >> (n - shift))
            value = result

        t >>= 1
        if t:
            doubled = set()
            for shift in shifts:
                doubled.symmetric_difference_update(((2 * shift) % n,))
            shifts = doubled

    return format(value, f"0{n}b")
