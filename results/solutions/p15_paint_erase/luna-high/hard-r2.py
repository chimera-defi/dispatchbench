def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coords = {1, n + 1}
    for op in ops:
        coords.add(op[1])
        coords.add(op[2] + 1)

    xs = sorted(coords)
    index = {x: i for i, x in enumerate(xs)}
    m = len(xs) - 1

    prefix = [0] * (m + 1)
    for i in range(m):
        prefix[i + 1] = prefix[i] + xs[i + 1] - xs[i]

    size = 4 * m + 5
    inf = 10**30
    mn = [0] * size
    second = [inf] * size
    count_min = [0] * size
    assigned = [-1] * size

    def build(node: int, left: int, right: int) -> None:
        count_min[node] = prefix[right] - prefix[left]
        if right - left > 1:
            mid = (left + right) // 2
            build(node * 2, left, mid)
            build(node * 2 + 1, mid, right)

    build(1, 0, m)

    def set_zero(node: int, left: int, right: int) -> None:
        mn[node] = 0
        second[node] = inf
        count_min[node] = prefix[right] - prefix[left]
        assigned[node] = 0

    def raise_min(node: int, color: int) -> None:
        mn[node] = color

    def push(node: int, left: int, right: int) -> None:
        mid = (left + right) // 2
        a, b = node * 2, node * 2 + 1

        if assigned[node] != -1:
            set_zero(a, left, mid)
            set_zero(b, mid, right)
            assigned[node] = -1

        if mn[a] < mn[node]:
            raise_min(a, mn[node])
        if mn[b] < mn[node]:
            raise_min(b, mn[node])

    def pull(node: int) -> None:
        a, b = node * 2, node * 2 + 1
        if mn[a] < mn[b]:
            mn[node] = mn[a]
            count_min[node] = count_min[a]
            second[node] = min(second[a], mn[b])
        elif mn[b] < mn[a]:
            mn[node] = mn[b]
            count_min[node] = count_min[b]
            second[node] = min(mn[a], second[b])
        else:
            mn[node] = mn[a]
            count_min[node] = count_min[a] + count_min[b]
            second[node] = min(second[a], second[b])
        assigned[node] = -1

    def paint_range(
        node: int, left: int, right: int, ql: int, qr: int, color: int
    ) -> None:
        if qr <= left or right <= ql or mn[node] >= color:
            return

        if ql <= left and right <= qr and color < second[node]:
            raise_min(node, color)
            return

        if right - left == 1:
            raise_min(node, color)
            return

        push(node, left, right)
        mid = (left + right) // 2
        paint_range(node * 2, left, mid, ql, qr, color)
        paint_range(node * 2 + 1, mid, right, ql, qr, color)
        pull(node)

    def erase_range(
        node: int, left: int, right: int, ql: int, qr: int
    ) -> None:
        if qr <= left or right <= ql:
            return
        if ql <= left and right <= qr:
            set_zero(node, left, right)
            return
        push(node, left, right)
        mid = (left + right) // 2
        erase_range(node * 2, left, mid, ql, qr)
        erase_range(node * 2 + 1, mid, right, ql, qr)
        pull(node)

    for op in ops:
        ql = index[op[1]]
        qr = index[op[2] + 1]
        if op[0] == 1:
            paint_range(1, 0, m, ql, qr, op[3])
        else:
            erase_range(1, 0, m, ql, qr)

    totals = {}

    def collect(node: int, left: int, right: int) -> None:
        if second[node] == inf:
            color = mn[node]
            if color:
                totals[color] = totals.get(color, 0) + prefix[right] - prefix[left]
            return
        push(node, left, right)
        mid = (left + right) // 2
        collect(node * 2, left, mid)
        collect(node * 2 + 1, mid, right)

    collect(1, 0, m)
    return [[color, totals[color]] for color in sorted(totals)]
