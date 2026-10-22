def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Sweep cell boundaries, maintaining the active operations in time order.
    m = len(ops)
    size = 1 << (m - 1).bit_length()
    colours = [0] * (2 * size)
    has_erase = bytearray(2 * size)

    events = []
    for i, op in enumerate(ops):
        leaf = size + i
        value = op[3] if op[0] == 1 else -1
        events.append((op[1], leaf, value))
        events.append((op[2] + 1, leaf, 0))
    events.sort()

    counts = {}
    previous = 1

    for position, node, value in events:
        colour = colours[1]
        if colour and position > previous:
            counts[colour] = counts.get(colour, 0) + position - previous
        previous = position

        has_erase[node] = value == -1
        colours[node] = value if value > 0 else 0
        node >>= 1

        while node:
            left = node << 1
            right = left | 1

            # A later erase discards all colours from earlier operations.
            if has_erase[right]:
                merged_colour = colours[right]
            else:
                merged_colour = max(colours[left], colours[right])
            merged_erase = has_erase[left] | has_erase[right]

            if (colours[node] == merged_colour
                    and has_erase[node] == merged_erase):
                break

            colours[node] = merged_colour
            has_erase[node] = merged_erase
            node >>= 1

    return [[colour, counts[colour]] for colour in sorted(counts)]
