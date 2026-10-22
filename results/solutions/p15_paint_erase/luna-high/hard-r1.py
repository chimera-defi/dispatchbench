def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    endpoints = {1, n + 1}
    for op in ops:
        endpoints.add(op[1])
        endpoints.add(op[2] + 1)

    coords = sorted(endpoints)
    index = {x: i for i, x in enumerate(coords)}
    size = len(coords) - 1
    if size <= 0:
        return []

    inf = 10**18
    capacity = 4 * size
    mn = [inf] * capacity
    second = [inf] * capacity
    min_weight = [0] * capacity
    total_weight = [0] * capacity

    def build(node: int, left: int, right: int) -> None:
        if right - left == 1:
            weight = coords[right] - coords[left]
            mn[node] = 0
            min_weight[node] = weight
            total_weight[node] = weight
            return
        mid = (left + right) // 2
        build(node * 2, left, mid)
        build(node * 2 + 1, mid, right)
        pull(node)

    def pull(node: int) -> None:
        a, b = node * 2, node * 2 + 1
        total_weight[node] = total_weight[a] + total_weight[b]
        mn[node] = min(mn[a], mn[b])
        min_weight[node] = 0
        second[node] = inf
        for child in (a, b):
            if mn[child] == mn[node]:
                min_weight[node] += min_weight[child]
                second[node] = min(second[node], second[child])
            else:
                second[node] = min(second[node], mn[child])

    def raise_min(node: int, value: int) -> None:
        mn[node] = value

    def push(node: int) -> None:
        floor = mn[node]
        for child in (node * 2, node * 2 + 1):
            if total_weight[child] and mn[child] < floor:
                raise_min(child, floor)

    def chmax(node: int, left: int, right: int,
              ql: int, qr: int, value: int) -> None:
        if qr <= left or right <= ql or not total_weight[node] or value <= mn[node]:
            return
        if ql <= left and right <= qr and value < second[node]:
            raise_min(node, value)
            return
        if right - left == 1:
            raise_min(node, value)
            return
        push(node)
        mid = (left + right) // 2
        chmax(node * 2, left, mid, ql, qr, value)
        chmax(node * 2 + 1, mid, right, ql, qr, value)
        pull(node)

    counts = {}

    def clear(node: int) -> None:
        mn[node] = second[node] = inf
        min_weight[node] = total_weight[node] = 0

    def deactivate(node: int, left: int, right: int,
                   ql: int, qr: int) -> None:
        if qr <= left or right <= ql or not total_weight[node]:
            return
        if ql <= left and right <= qr:
            if second[node] == inf:
                if mn[node] > 0:
                    counts[mn[node]] = counts.get(mn[node], 0) + total_weight[node]
                clear(node)
                return
            if right - left == 1:
                if mn[node] > 0:
                    counts[mn[node]] = counts.get(mn[node], 0) + total_weight[node]
                clear(node)
                return
        if right - left == 1:
            if mn[node] > 0:
                counts[mn[node]] = counts.get(mn[node], 0) + total_weight[node]
            clear(node)
            return
        push(node)
        mid = (left + right) // 2
        deactivate(node * 2, left, mid, ql, qr)
        deactivate(node * 2 + 1, mid, right, ql, qr)
        pull(node)

    build(1, 0, size)

    for op in reversed(ops):
        left = index[op[1]]
        right = index[op[2] + 1]
        if op[0] == 1:
            chmax(1, 0, size, left, right, op[3])
        else:
            deactivate(1, 0, size, left, right)

    deactivate(1, 0, size, 0, size)
    return [[color, counts[color]] for color in sorted(counts)]
