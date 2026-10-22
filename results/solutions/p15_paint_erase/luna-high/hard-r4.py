def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coords = {1, n + 1}
    for op in ops:
        coords.add(op[1])
        coords.add(op[2] + 1)

    coords = sorted(coords)
    index = {x: i for i, x in enumerate(coords)}
    size = len(coords) - 1

    inf = 10**30
    mn = [0] * (4 * size)
    second = [inf] * (4 * size)
    count = [0] * (4 * size)
    lazy_assign = [-1] * (4 * size)

    lengths = [coords[i + 1] - coords[i] for i in range(size)]
    prefix = [0] * (size + 1)
    for i, length in enumerate(lengths):
        prefix[i + 1] = prefix[i] + length

    def total_weight(left: int, right: int) -> int:
        return prefix[right + 1] - prefix[left]

    def build(node: int, left: int, right: int) -> None:
        count[node] = total_weight(left, right)
        if left == right:
            return
        mid = (left + right) // 2
        build(node * 2, left, mid)
        build(node * 2 + 1, mid + 1, right)

    build(1, 0, size - 1)

    def apply_assign(node: int, left: int, right: int, value: int) -> None:
        mn[node] = value
        second[node] = inf
        count[node] = total_weight(left, right)
        lazy_assign[node] = value

    def apply_raise(node: int, value: int) -> None:
        if value <= mn[node]:
            return
        mn[node] = value

    def pull(node: int) -> None:
        a = node * 2
        b = a + 1
        if mn[a] < mn[b]:
            mn[node] = mn[a]
            count[node] = count[a]
            second[node] = min(second[a], mn[b])
        elif mn[b] < mn[a]:
            mn[node] = mn[b]
            count[node] = count[b]
            second[node] = min(mn[a], second[b])
        else:
            mn[node] = mn[a]
            count[node] = count[a] + count[b]
            second[node] = min(second[a], second[b])

    def push(node: int, left: int, right: int) -> None:
        if left == right:
            return
        mid = (left + right) // 2
        a = node * 2
        b = a + 1

        if lazy_assign[node] != -1:
            value = lazy_assign[node]
            apply_assign(a, left, mid, value)
            apply_assign(b, mid + 1, right, value)
            lazy_assign[node] = -1

        if mn[a] < mn[node]:
            apply_raise(a, mn[node])
        if mn[b] < mn[node]:
            apply_raise(b, mn[node])

    def range_assign(node: int, left: int, right: int,
                     ql: int, qr: int, value: int) -> None:
        if ql <= left and right <= qr:
            apply_assign(node, left, right, value)
            return
        push(node, left, right)
        mid = (left + right) // 2
        if ql <= mid:
            range_assign(node * 2, left, mid, ql, qr, value)
        if qr > mid:
            range_assign(node * 2 + 1, mid + 1, right, ql, qr, value)
        pull(node)

    def range_chmax(node: int, left: int, right: int,
                    ql: int, qr: int, value: int) -> None:
        if value <= mn[node]:
            return
        if ql <= left and right <= qr and value < second[node]:
            apply_raise(node, value)
            return
        if left == right:
            apply_raise(node, value)
            return
        push(node, left, right)
        mid = (left + right) // 2
        if ql <= mid:
            range_chmax(node * 2, left, mid, ql, qr, value)
        if qr > mid:
            range_chmax(node * 2 + 1, mid + 1, right, ql, qr, value)
        pull(node)

    for op in ops:
        left = index[op[1]]
        right = index[op[2] + 1] - 1
        if op[0] == 0:
            range_assign(1, 0, size - 1, left, right, 0)
        else:
            range_chmax(1, 0, size - 1, left, right, op[3])

    histogram = {}

    def collect(node: int, left: int, right: int) -> None:
        if left == right:
            value = mn[node]
            if value:
                histogram[value] = histogram.get(value, 0) + lengths[left]
            return
        push(node, left, right)
        mid = (left + right) // 2
        collect(node * 2, left, mid)
        collect(node * 2 + 1, mid + 1, right)

    collect(1, 0, size - 1)
    return [[colour, histogram[colour]] for colour in sorted(histogram)]
