def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    size = 1
    while size < len(ops):
        size <<= 1

    values = [0] * (2 * size)
    resets = bytearray(2 * size)
    events = []

    for i, op in enumerate(ops):
        kind, left, right = op[:3]
        colour = op[3] if kind == 1 else -1
        events.append((left, size + i, colour))
        events.append((right + 1, size + i, 0))

    events.sort()
    counts = {}
    previous = 1

    # Each node represents its operations in chronological order:
    # either x -> max(x, value), or x -> value when a reset occurs.
    for position, leaf, colour in events:
        if position > previous:
            current = values[1]
            if current:
                counts[current] = (
                    counts.get(current, 0) + position - previous
                )
            previous = position

        values[leaf] = max(colour, 0)
        resets[leaf] = colour == -1

        node = leaf >> 1
        while node:
            left = node << 1
            right = left | 1

            new_reset = resets[left] | resets[right]
            if resets[right]:
                new_value = values[right]
            else:
                new_value = max(values[left], values[right])

            if values[node] == new_value and resets[node] == new_reset:
                break

            values[node] = new_value
            resets[node] = new_reset
            node >>= 1

    return [[colour, counts[colour]] for colour in sorted(counts)]
