def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    m = len(ops)
    size = 1
    while size < m:
        size <<= 1

    colours = [0] * (2 * size)
    has_erase = bytearray(2 * size)

    events = []
    for i, op in enumerate(ops):
        events.append((op[1], i))
        events.append((op[2] + 1, ~i))
    events.sort()

    counts = {}
    previous = 1

    for position, event_id in events:
        if position > previous:
            colour = colours[1]
            if colour:
                counts[colour] = (
                    counts.get(colour, 0) + position - previous
                )
            previous = position

        if event_id >= 0:
            op = ops[event_id]
            node = size + event_id
            if op[0] == 0:
                colours[node] = 0
                has_erase[node] = 1
            else:
                colours[node] = op[3]
                has_erase[node] = 0
        else:
            node = size + (~event_id)
            colours[node] = 0
            has_erase[node] = 0

        node >>= 1
        while node:
            left = node << 1
            right = left | 1

            # The right subtree contains the later operations.
            erased = has_erase[left] | has_erase[right]
            colour = colours[right]
            if not has_erase[right] and colours[left] > colour:
                colour = colours[left]

            if colours[node] == colour and has_erase[node] == erased:
                break

            colours[node] = colour
            has_erase[node] = erased
            node >>= 1

    return [[colour, counts[colour]] for colour in sorted(counts)]
