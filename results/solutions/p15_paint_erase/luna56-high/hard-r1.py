def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    points = {1, n + 1}
    for op in ops:
        points.add(op[1])
        points.add(op[2] + 1)

    coords = sorted(points)
    m = len(coords) - 1
    size = 4 * m + 5
    inf = 10**19

    mn = [0] * size
    smn = [inf] * size
    cmn = [0] * size
    lazy = [-1] * size

    def build(p: int, l: int, r: int) -> None:
        cmn[p] = coords[r] - coords[l]
        if r - l > 1:
            mid = (l + r) // 2
            build(p * 2, l, mid)
            build(p * 2 + 1, mid, r)

    def assign(p: int, value: int, length: int) -> None:
        mn[p] = value
        smn[p] = inf
        cmn[p] = length
        lazy[p] = value

    def raise_min(p: int, value: int) -> None:
        if value <= mn[p]:
            return
        mn[p] = value
        if lazy[p] != -1:
            lazy[p] = value

    def push(p: int, l: int, r: int) -> None:
        if r - l <= 1:
            return

        left = p * 2
        right = left + 1
        mid = (l + r) // 2

        if lazy[p] != -1:
            value = lazy[p]
            assign(left, value, coords[mid] - coords[l])
            assign(right, value, coords[r] - coords[mid])
            lazy[p] = -1

        cap = mn[p]
        if mn[left] < cap:
            raise_min(left, cap)
        if mn[right] < cap:
            raise_min(right, cap)

    def pull(p: int) -> None:
        left = p * 2
        right = left + 1

        if mn[left] < mn[right]:
            mn[p] = mn[left]
            cmn[p] = cmn[left]
            smn[p] = min(smn[left], mn[right])
        elif mn[left] > mn[right]:
            mn[p] = mn[right]
            cmn[p] = cmn[right]
            smn[p] = min(mn[left], smn[right])
        else:
            mn[p] = mn[left]
            cmn[p] = cmn[left] + cmn[right]
            smn[p] = min(smn[left], smn[right])

    def range_assign_zero(p: int, ql: int, qr: int, l: int, r: int) -> None:
        if qr <= l or r <= ql:
            return
        if ql <= l and r <= qr:
            assign(p, 0, coords[r] - coords[l])
            return

        push(p, l, r)
        mid = (l + r) // 2
        range_assign_zero(p * 2, ql, qr, l, mid)
        range_assign_zero(p * 2 + 1, ql, qr, mid, r)
        pull(p)

    def range_chmax(
        p: int, ql: int, qr: int, value: int, l: int, r: int
    ) -> None:
        if qr <= l or r <= ql or value <= mn[p]:
            return

        if ql <= l and r <= qr and value < smn[p]:
            raise_min(p, value)
            return

        push(p, l, r)
        mid = (l + r) // 2
        range_chmax(p * 2, ql, qr, value, l, mid)
        range_chmax(p * 2 + 1, ql, qr, value, mid, r)
        pull(p)

    build(1, 0, m)

    for op in ops:
        if op[0] == 1:
            left = bisect_left(coords, op[1])
            right = bisect_left(coords, op[2] + 1)
            range_chmax(1, left, right, op[3], 0, m)
        else:
            left = bisect_left(coords, op[1])
            right = bisect_left(coords, op[2] + 1)
            range_assign_zero(1, left, right, 0, m)

    counts = {}

    def collect(p: int, l: int, r: int) -> None:
        if smn[p] == inf:
            value = mn[p]
            if value:
                counts[value] = counts.get(value, 0) + coords[r] - coords[l]
            return

        mid = (l + r) // 2
        collect(p * 2, l, mid)
        collect(p * 2 + 1, mid, r)

    collect(1, 0, m)
    return [[color, counts[color]] for color in sorted(counts)]
