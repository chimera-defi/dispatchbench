def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    if t == 0:
        return state

    active = set()
    for offset in offsets:
        d = offset % n
        if d in active:
            active.remove(d)
        else:
            active.add(d)

    if not active:
        return "0" * n

    value = int(state[::-1], 2)
    mask = (1 << n) - 1

    while t:
        if t & 1:
            next_value = 0
            for d in active:
                rotated = ((value >> d) | (value << (n - d))) & mask
                next_value ^= rotated
            value = next_value

            if value == 0:
                return "0" * n

        t >>= 1
        if not t:
            break

        doubled = set()
        for d in active:
            d = (2 * d) % n
            if d in doubled:
                doubled.remove(d)
            else:
                doubled.add(d)
        active = doubled

    return format(value, f"0{n}b")[::-1]
