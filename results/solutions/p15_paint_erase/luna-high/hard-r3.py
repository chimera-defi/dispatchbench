def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    boundaries = {1, n + 1}
    for op in ops:
        boundaries.add(op[1])
        boundaries.add(op[2] + 1)

    points = sorted(boundaries)
    index = {x: i for i, x in enumerate(points)}
    size = len(points) - 1

    inf = 10**18
    min1 = [0] * (4 * size)
    min2 = [inf] * (4 * size)

    def apply_chmax(node: int, value: int) -> None:
        if min1[node] < value:
            min1[node] = value

    def push(node: int) -> None:
        value = min1[node]
        left = node * 2
        if min1[left] < value:
            apply_chmax(left, value)
        if min1[left + 1] < value:
            apply_chmax(left + 1, value)

    def pull(node: int) -> None:
        left, right = node * 2, node * 2 + 1
        low = min(min1[left], min1[right])
        min1[node] = low
        min2[node] = min(
            min2[left] if min1[left] == low else min1[left],
            min2[right] if min1[right] == low else min1[right],
        )

    def range_chmax(node: int, lo: int, hi: int,
                    qlo: int, qhi: int, value: int) -> None:
        if qhi <= lo or hi <= qlo or value <= min1[node]:
            return
        if qlo <= lo and hi <= qhi and value < min2[node]:
            apply_chmax(node, value)
            return
        if hi - lo == 1:
            apply_chmax(node, value)
            return
        push(node)
        mid = (lo + hi) // 2
        range_chmax(node * 2, lo, mid, qlo, qhi, value)
        range_chmax(node * 2 + 1, mid, hi, qlo, qhi, value)
        pull(node)

    def point_value(node: int, lo: int, hi: int, pos: int) -> int:
        if hi - lo == 1:
            return min1[node]
        push(node)
        mid = (lo + hi) // 2
        if pos < mid:
            return point_value(node * 2, lo, mid, pos)
        return point_value(node * 2 + 1, mid, hi, pos)

    next_unresolved = list(range(size + 1))

    def find(pos: int) -> int:
        root = pos
        while next_unresolved[root] != root:
            root = next_unresolved[root]
        while next_unresolved[pos] != pos:
            nxt = next_unresolved[pos]
            next_unresolved[pos] = root
            pos = nxt
        return root

    totals = {}

    for op in reversed(ops):
        left = index[op[1]]
        right = index[op[2] + 1]

        if op[0] == 1:
            range_chmax(1, 0, size, left, right, op[3])
        else:
            pos = find(left)
            while pos < right:
                color = point_value(1, 0, size, pos)
                if color:
                    length = points[pos + 1] - points[pos]
                    totals[color] = totals.get(color, 0) + length
                next_unresolved[pos] = find(pos + 1)
                pos = find(pos)

    pos = find(0)
    while pos < size:
        color = point_value(1, 0, size, pos)
        if color:
            length = points[pos + 1] - points[pos]
            totals[color] = totals.get(color, 0) + length
        next_unresolved[pos] = find(pos + 1)
        pos = find(pos)

    return [[color, totals[color]] for color in sorted(totals)]
