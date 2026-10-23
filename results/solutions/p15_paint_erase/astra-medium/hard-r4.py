def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    import heapq

    m = len(ops)
    events = []
    for i, op in enumerate(ops):
        events.append((op[1], i))
        events.append((op[2] + 1, ~i))
    events.sort()

    size = 1 << (m - 1).bit_length()
    tree = [0] * (2 * size)
    active_erases = bytearray(m)
    erase_heap = []
    counts = {}

    previous = 1
    colour = 0
    k = 0
    total_events = len(events)

    while k < total_events:
        position = events[k][0]
        if colour and position > previous:
            counts[colour] = counts.get(colour, 0) + position - previous

        while k < total_events and events[k][0] == position:
            encoded = events[k][1]
            starting = encoded >= 0
            i = encoded if starting else ~encoded
            op = ops[i]

            if op[0] == 0:
                active_erases[i] = starting
                if starting:
                    heapq.heappush(erase_heap, -i)
            else:
                node = size + i
                tree[node] = op[3] if starting else 0
                node >>= 1
                while node:
                    value = max(tree[node << 1], tree[node << 1 | 1])
                    if tree[node] == value:
                        break
                    tree[node] = value
                    node >>= 1

            k += 1

        if k == total_events:
            break

        while erase_heap and not active_erases[-erase_heap[0]]:
            heapq.heappop(erase_heap)

        if not erase_heap:
            colour = tree[1]
        else:
            # Only paints occurring after the latest covering erase count.
            node = size - erase_heap[0]
            colour = 0
            while node > 1:
                if node & 1 == 0:
                    colour = max(colour, tree[node + 1])
                node >>= 1

        previous = position

    return [[c, counts[c]] for c in sorted(counts)]
