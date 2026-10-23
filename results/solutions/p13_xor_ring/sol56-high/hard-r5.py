def evolve(state: str, offsets: list[int], t: int) -> str:
    n = len(state)
    current = bytearray(c == "1" for c in state)

    active = set()
    for offset in offsets:
        shift = offset % n
        if shift in active:
            active.remove(shift)
        else:
            active.add(shift)

    while t:
        if t & 1:
            if not active:
                return "0" * n

            next_state = bytearray(n)
            for shift in active:
                split = n - shift
                for i in range(split):
                    next_state[i] ^= current[i + shift]
                for i in range(split, n):
                    next_state[i] ^= current[i - split]
            current = next_state

        t >>= 1
        if not t:
            break

        squared = set()
        for shift in active:
            doubled = (2 * shift) % n
            if doubled in squared:
                squared.remove(doubled)
            else:
                squared.add(doubled)
        active = squared

    return "".join("1" if value else "0" for value in current)
