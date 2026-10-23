def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    if t == 0:
        return state

    active = set()
    for offset in offsets:
        shift = offset % n
        if shift in active:
            active.remove(shift)
        else:
            active.add(shift)

    if not active:
        return "0" * n

    current = [c == "1" for c in state]
    scale = 1

    while t:
        if t & 1:
            shifts = set()
            for offset in active:
                shift = (offset * scale) % n
                if shift in shifts:
                    shifts.remove(shift)
                else:
                    shifts.add(shift)

            if not shifts:
                return "0" * n

            nxt = [False] * n
            for shift in shifts:
                for i in range(n):
                    nxt[i] ^= current[(i + shift) % n]
            current = nxt

        t >>= 1
        scale = (scale * 2) % n

    return "".join("1" if value else "0" for value in current)
