def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coords_set = {1, n + 1}
    for op in ops:
        coords_set.add(op[1])
        coords_set.add(op[2] + 1)

    coords = sorted(coords_set)
    m = len(coords) - 1
    pos = {x: i for i, x in enumerate(coords)}

    size = 4 * m + 5
    INF = 10**18

    mn = [0] * size
    smn = [INF] * size
    cnt = [0] * size
    lazy = [-1] * size

    def build(p: int, left: int, right: int) -> None:
        cnt[p] = right - left + 1
        if left != right:
            mid = (left + right) // 2
            build(p * 2, left, mid)
            build(p * 2 + 1, mid + 1, right)

    def apply_assign(p: int, value: int, length: int) -> None:
        mn[p] = value
        smn[p] = INF
        cnt[p] = length
        lazy[p] = value

    def apply_chmax(p: int, value: int) -> None:
        if mn[p] >= value:
            return
        mn[p] = value
        if lazy[p] != -1:
            lazy[p] = value

    def push(p: int, left: int, right: int) -> None:
        if left == right:
            lazy[p] = -1
            return

        mid = (left + right) // 2
        lc = p * 2
        rc = lc + 1

        if lazy[p] != -1:
            value = lazy[p]
            apply_assign(lc, value, mid - left + 1)
            apply_assign(rc, value, right - mid)
            lazy[p] = -1

        if mn[lc] < mn[p]:
            apply_chmax(lc, mn[p])
        if mn[rc] < mn[p]:
            apply_chmax(rc, mn[p])

    def pull(p: int) -> None:
        lc = p * 2
        rc = lc + 1

        if mn[lc] < mn[rc]:
            mn[p] = mn[lc]
            cnt[p] = cnt[lc]
            smn[p] = min(smn[lc], mn[rc])
        elif mn[rc] < mn[lc]:
            mn[p] = mn[rc]
            cnt[p] = cnt[rc]
            smn[p] = min(mn[lc], smn[rc])
        else:
            mn[p] = mn[lc]
            cnt[p] = cnt[lc] + cnt[rc]
            smn[p] = min(smn[lc], smn[rc])

    def range_chmax(
        p: int, left: int, right: int,
        ql: int, qr: int, value: int
    ) -> None:
        if right < ql or qr < left or mn[p] >= value:
            return

        if ql <= left and right <= qr and value < smn[p]:
            apply_chmax(p, value)
            return

        if left == right:
            apply_chmax(p, value)
            return

        push(p, left, right)
        mid = (left + right) // 2
        range_chmax(p * 2, left, mid, ql, qr, value)
        range_chmax(p * 2 + 1, mid + 1, right, ql, qr, value)
        pull(p)

    def range_assign(
        p: int, left: int, right: int,
        ql: int, qr: int, value: int
    ) -> None:
        if right < ql or qr < left:
            return

        if ql <= left and right <= qr:
            apply_assign(p, value, right - left + 1)
            return

        push(p, left, right)
        mid = (left + right) // 2
        range_assign(p * 2, left, mid, ql, qr, value)
        range_assign(p * 2 + 1, mid + 1, right, ql, qr, value)
        pull(p)

    build(1, 0, m - 1)

    for op in ops:
        left = pos[op[1]]
        right = pos[op[2] + 1] - 1

        if op[0] == 0:
            range_assign(1, 0, m - 1, left, right, 0)
        else:
            range_chmax(1, 0, m - 1, left, right, op[3])

    result = {}

    def collect(p: int, left: int, right: int) -> None:
        if smn[p] == INF:
            if mn[p] != 0:
                length = coords[right + 1] - coords[left]
                result[mn[p]] = result.get(mn[p], 0) + length
            return

        push(p, left, right)
        mid = (left + right) // 2
        collect(p * 2, left, mid)
        collect(p * 2 + 1, mid + 1, right)

    collect(1, 0, m - 1)
    return [[color, result[color]] for color in sorted(result)]
