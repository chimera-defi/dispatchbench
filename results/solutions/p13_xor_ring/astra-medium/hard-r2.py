def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    value = int(state, 2)

    shifts = set()
    for offset in offsets:
        d = offset % n
        if d in shifts:
            shifts.remove(d)
        else:
            shifts.add(d)

    while t:
        if not shifts or value == 0:
            return "0" * n

        if t & 1:
            result = 0
            for d in shifts:
                result ^= ((value << d) & mask) | (value >> (n - d))
            value = result

        t >>= 1
        if t:
            # Over XOR, squaring cancels all cross terms.
            doubled = set()
            for d in shifts:
                d = (2 * d) % n
                if d in doubled:
                    doubled.remove(d)
                else:
                    doubled.add(d)
            shifts = doubled

    return format(value, f"0{n}b")
