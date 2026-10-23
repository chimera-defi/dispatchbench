def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)

    shifts = set()
    for offset in offsets:
        shift = offset % n
        if shift in shifts:
            shifts.remove(shift)
        else:
            shifts.add(shift)

    if t == 0:
        return state
    if not shifts:
        return "0" * n

    current = bytearray(c == "1" for c in state)

    while t:
        if t & 1:
            nxt = bytearray(n)
            for shift in shifts:
                for i in range(n):
                    nxt[i] ^= current[(i + shift) % n]
            current = nxt

        t >>= 1
        if t:
            squared = set()
            for shift in shifts:
                doubled = (shift * 2) % n
                if doubled in squared:
                    squared.remove(doubled)
                else:
                    squared.add(doubled)
            shifts = squared
            if not shifts:
                return "0" * n

    return bytes(48 + bit for bit in current).decode()
