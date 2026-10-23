def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    m = len(ops)
    size = 1 << (m - 1).bit_length()
    tree = [0] * (2 * size)
    events = []

    # Operations are leaves in chronological order.
    # A nonnegative value means no erase, with that maximum colour.
    # A negative value -(c + 1) means an erase occurred, followed by
    # a maximum colour of c (where c = 0 means blank).
    for i, op in enumerate(ops):
        l, r = op[1], op[2]
        value = op[3] if op[0] == 1 else -1
        events.append((l, i, value))
        events.append((r + 1, i, 0))

    events.sort()
    counts = {}
    previous = 1

    for position, index, value in events:
        if position != previous:
            result = tree[1]
            colour = result if result >= 0 else -result - 1
            if colour:
                counts[colour] = counts.get(colour, 0) + position - previous
            previous = position

        node = size + index
        tree[node] = value
        node >>= 1

        while node:
            left = tree[node * 2]
            right = tree[node * 2 + 1]

            if right < 0:
                combined = right
            elif left < 0:
                combined = min(left, -right - 1)
            else:
                combined = max(left, right)

            if tree[node] == combined:
                break
            tree[node] = combined
            node >>= 1

    return [[colour, counts[colour]] for colour in sorted(counts)]
