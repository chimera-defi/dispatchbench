def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    m = len(ops)
    size = 1
    while size < m:
        size <<= 1

    # Each node records whether it contains an active erase and the
    # greatest active paint colour after its last active erase.
    has_erase = [False] * (2 * size)
    colour = [0] * (2 * size)

    events = []
    for i, op in enumerate(ops):
        l, r = op[1], op[2]
        value = op[3] if op[0] == 1 else -1
        events.append((l, i, value))
        events.append((r + 1, i, 0))
    events.sort()

    counts = {}
    previous = 1

    for position, index, value in events:
        current = colour[1]
        if position > previous and current:
            counts[current] = counts.get(current, 0) + position - previous
        previous = position

        node = size + index
        has_erase[node] = value == -1
        colour[node] = value if value > 0 else 0
        node >>= 1

        while node:
            left = node << 1
            right = left | 1

            erased = has_erase[left] or has_erase[right]
            if has_erase[right]:
                best = colour[right]
            else:
                best = max(colour[left], colour[right])

            if has_erase[node] == erased and colour[node] == best:
                break

            has_erase[node] = erased
            colour[node] = best
            node >>= 1

    return [[c, counts[c]] for c in sorted(counts)]
