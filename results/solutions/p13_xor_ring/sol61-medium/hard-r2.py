def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    mask = (1 << n) - 1
    value = int(state[::-1], 2)

    shifts = set()
    for offset in offsets:
        shift = offset % n
        if shift in shifts:
            shifts.remove(shift)
        else:
            shifts.add(shift)

    # Over XOR, squaring a sum of rotations doubles every rotation.
    while t and value and shifts:
        if t & 1:
            result = 0
            for shift in shifts:
                result ^= ((value >> shift) | (value << (n - shift))) & mask
            value = result

        t >>= 1
        if t:
            doubled = set()
            for shift in shifts:
                shift = (2 * shift) % n
                if shift in doubled:
                    doubled.remove(shift)
                else:
                    doubled.add(shift)
            shifts = doubled

    if t and not shifts:
        value = 0

    return format(value, f"0{n}b")[::-1]
