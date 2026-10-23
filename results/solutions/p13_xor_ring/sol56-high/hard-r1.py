def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    if t == 0:
        return state

    shifts = set()
    for offset in offsets:
        shift = offset % n
        if shift in shifts:
            shifts.remove(shift)
        else:
            shifts.add(shift)

    current = [ord(c) - ord("0") for c in state]

    while t:
        if t & 1:
            if not shifts:
                return "0" * n

            updated = [0] * n
            for shift in shifts:
                split = n - shift
                for i in range(split):
                    updated[i] ^= current[i + shift]
                for i in range(split, n):
                    updated[i] ^= current[i - split]
            current = updated

        t >>= 1
        if t:
            doubled = set()
            for shift in shifts:
                shift = (shift * 2) % n
                if shift in doubled:
                    doubled.remove(shift)
                else:
                    doubled.add(shift)
            shifts = doubled

    return "".join(map(str, current))
