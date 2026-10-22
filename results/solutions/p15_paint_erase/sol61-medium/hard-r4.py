def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    m = len(ops)
    size = 1 << (m - 1).bit_length()

    # Each node describes its active operations in chronological order.
    # value: maximum paint colour following its last erase.
    # erased: whether it contains an erase.
    value = [0] * (2 * size)
    erased = bytearray(2 * size)

    events = []
    for i, op in enumerate(ops):
        kind, l, r = op[:3]
        colour = op[3] if kind else -1
        events.append((l, i, colour))
        events.append((r + 1, i, 0))
    events.sort()

    counts = {}
    previous = 1

    for position, index, colour in events:
        if position != previous:
            current = value[1]
            if current:
                counts[current] = counts.get(current, 0) + position - previous
            previous = position

        node = size + index
        value[node] = colour if colour > 0 else 0
        erased[node] = colour == -1
        node >>= 1

        while node:
            left = node << 1
            right = left | 1

            new_erased = erased[left] | erased[right]
            if erased[right]:
                new_value = value[right]
            else:
                a = value[left]
                b = value[right]
                new_value = a if a >= b else b

            if value[node] == new_value and erased[node] == new_erased:
                break

            value[node] = new_value
            erased[node] = new_erased
            node >>= 1

    return [[colour, counts[colour]] for colour in sorted(counts)]
