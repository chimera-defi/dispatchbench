def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    if t == 0:
        return state

    mask = (1 << n) - 1
    current = int(state[::-1], 2)
    shifts = [d % n for d in offsets]

    while t:
        if t & 1:
            updated = 0
            for shift in shifts:
                rotated = ((current >> shift) |
                           (current << (n - shift))) & mask
                updated ^= rotated
            current = updated

        shifts = [(2 * shift) % n for shift in shifts]
        t >>= 1

    return format(current, f"0{n}b")[::-1]
