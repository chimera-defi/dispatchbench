def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    coords = [1, n + 1]
    for op in ops:
        coords.append(op[1])
        coords.append(op[2] + 1)

    coords = sorted(set(coords))
    index = {x: i for i, x in enumerate(coords)}
    m = len(coords) - 1

    erase_events = []
    paint_events = []

    for time, op in enumerate(ops, 1):
        left = index[op[1]]
        right = index[op[2] + 1] - 1

        if op[0] == 0:
            erase_events.append((time, left, right))
        else:
            paint_events.append((op[3], time, left, right))

    if not paint_events:
        return []

    last_erase = [0] * m
    parent = list(range(m + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for time, left, right in reversed(erase_events):
        i = find(left)
        while i <= right:
            last_erase[i] = time
            parent[i] = find(i + 1)
            i = parent[i]

    inf = 10**18
    size = 4 * m + 5
    seg_min = [inf] * size
    seg_max = [-1] * size

    def build(node, left, right):
        if left == right:
            value = last_erase[left]
            seg_min[node] = value
            seg_max[node] = value
            return

        mid = (left + right) // 2
        build(node * 2, left, mid)
        build(node * 2 + 1, mid + 1, right)

        seg_min[node] = min(seg_min[node * 2], seg_min[node * 2 + 1])
        seg_max[node] = max(seg_max[node * 2], seg_max[node * 2 + 1])

    build(1, 0, m - 1)

    counts = {}

    def assign(node, left, right, qleft, qright, time, color):
        if qright < left or right < qleft or seg_min[node] >= time:
            return

        if qleft <= left and right <= qright and seg_max[node] < time:
            counts[color] = counts.get(color, 0) + coords[right + 1] - coords[left]
            seg_min[node] = inf
            seg_max[node] = -1
            return

        if left == right:
            counts[color] = counts.get(color, 0) + coords[left + 1] - coords[left]
            seg_min[node] = inf
            seg_max[node] = -1
            return

        mid = (left + right) // 2

        if qleft <= mid:
            assign(node * 2, left, mid, qleft, qright, time, color)
        if qright > mid:
            assign(node * 2 + 1, mid + 1, right, qleft, qright, time, color)

        seg_min[node] = min(seg_min[node * 2], seg_min[node * 2 + 1])
        seg_max[node] = max(seg_max[node * 2], seg_max[node * 2 + 1])

    paint_events.sort(reverse=True)

    for color, time, left, right in paint_events:
        assign(1, 0, m - 1, left, right, time, color)

    return [[color, counts[color]] for color in sorted(counts)]
