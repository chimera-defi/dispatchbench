def evolve(state: str, offsets: list[int], t: int) -> str:
    if t == 0:
        return state

    n = len(state)
    shifts = set()
    for offset in offsets:
        shift = offset % n
        if shift in shifts:
            shifts.remove(shift)
        else:
            shifts.add(shift)

    current = bytearray(c == "1" for c in state)

    while t:
        if t & 1:
            if not shifts:
                return "0" * n

            if len(shifts) == 1:
                shift = next(iter(shifts))
                current = current[shift:] + current[:shift]
            else:
                nxt = bytearray(n)
                for shift in shifts:
                    j = shift
                    for i in range(n):
                        nxt[i] ^= current[j]
                        j += 1
                        if j == n:
                            j = 0
                current = nxt

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

    return "".join("1" if bit else "0" for bit in current)
