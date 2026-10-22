def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    m = len(ops)
    size = 1 << (m - 1).bit_length()

    # Each node summarizes its active operations in chronological order:
    # whether they contain an erase, and the maximum colour after the last erase.
    colour = [0] * (2 * size)
    erased = bytearray(2 * size)

    events = []
    for i, op in enumerate(ops):
        events.append((op[1], i))
        events.append((op[2] + 1, ~i))
    events.sort()

    counts = {}
    previous = events[0][0]

    for position, event in events:
        width = position - previous
        current = colour[1]
        if width and current:
            counts[current] = counts.get(current, 0) + width
        previous = position

        if event >= 0:
            index = event
            active = True
        else:
            index = ~event
            active = False

        node = size + index
        op = ops[index]
        if active:
            if op[0] == 0:
                colour[node] = 0
                erased[node] = 1
            else:
                colour[node] = op[3]
                erased[node] = 0
        else:
            colour[node] = 0
            erased[node] = 0

        node >>= 1
        while node:
            left = node << 1
            right = left | 1

            if erased[right]:
                new_colour = colour[right]
                new_erased = 1
            else:
                a = colour[left]
                b = colour[right]
                new_colour = a if a >= b else b
                new_erased = erased[left]

            if colour[node] == new_colour and erased[node] == new_erased:
                break

            colour[node] = new_colour
            erased[node] = new_erased
            node >>= 1

    return [[c, counts[c]] for c in sorted(counts)]
