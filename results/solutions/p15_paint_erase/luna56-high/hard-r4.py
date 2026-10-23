def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    coords = {1, n + 1}
    for op in ops:
        coords.add(op[1])
        coords.add(op[2] + 1)

    coords = sorted(coords)
    pos = {x: i for i, x in enumerate(coords)}
    m = len(coords) - 1

    size = 4 * m + 5
    INF = 10**18

    mn = [0] * size
    smn = [INF] * size
    cnt = [0] * size
    total = [0] * size
    lazy = [0] * size
    zero = [False] * size

    def build(p: int, l: int, r: int) -> None:
        if r - l == 1:
            total[p] = cnt[p] = coords[r] - coords[l]
            return
        mid = (l + r) // 2
        build(p * 2, l, mid)
        build(p * 2 + 1, mid, r)
        total[p] = total[p * 2] + total[p * 2 + 1]
        cnt[p] = total[p]

    def apply_zero(p: int) -> None:
        mn[p] = 0
        smn[p] = INF
        cnt[p] = total[p]
        lazy[p] = 0
        zero[p] = True

    def apply_chmax(p: int, value: int) -> None:
        if value <= mn[p]:
            return
        mn[p] = value
        lazy[p] = max(lazy[p], value)

    def pull(p: int) -> None:
        left = p * 2
        right = left + 1
        best = min(mn[left], mn[right])

        mn[p] = best
        cnt[p] = 0
        second = INF

        if mn[left] == best:
            cnt[p] += cnt[left]
            second = min(second, smn[left])
        else:
            second = min(second, mn[left])

        if mn[right] == best:
            cnt[p] += cnt[right]
            second = min(second, smn[right])
        else:
            second = min(second, mn[right])

        smn[p] = second

    def push(p: int) -> None:
        left = p * 2
        right = left + 1

        if zero[p]:
            apply_zero(left)
            apply_zero(right)
            zero[p] = False

        if lazy[p]:
            value = lazy[p]
            if value > mn[left]:
                apply_chmax(left, value)
            if value > mn[right]:
                apply_chmax(right, value)
            lazy[p] = 0

    def range_zero(p: int, l: int, r: int, ql: int, qr: int) -> None:
        if qr <= l or r <= ql:
            return
        if ql <= l and r <= qr:
            apply_zero(p)
            return

        push(p)
        mid = (l + r) // 2
        range_zero(p * 2, l, mid, ql, qr)
        range_zero(p * 2 + 1, mid, r, ql, qr)
        pull(p)

    def range_chmax(
        p: int, l: int, r: int, ql: int, qr: int, value: int
    ) -> None:
        if qr <= l or r <= ql or value <= mn[p]:
            return

        if ql <= l and r <= qr and value < smn[p]:
            apply_chmax(p, value)
            return

        push(p)
        mid = (l + r) // 2
        range_chmax(p * 2, l, mid, ql, qr, value)
        range_chmax(p * 2 + 1, mid, r, ql, qr, value)
        pull(p)

    def collect(
        p: int, l: int, r: int, result: dict[int, int]
    ) -> None:
        if smn[p] == INF:
            if mn[p] != 0:
                result[mn[p]] = result.get(mn[p], 0) + total[p]
            return

        push(p)
        mid = (l + r) // 2
        collect(p * 2, l, mid, result)
        collect(p * 2 + 1, mid, r, result)

    build(1, 0, m)

    for op in ops:
        left = pos[op[1]]
        right = pos[op[2] + 1]

        if op[0] == 0:
            range_zero(1, 0, m, left, right)
        else:
            range_chmax(1, 0, m, left, right, op[3])

    result = {}
    collect(1, 0, m, result)
    return [[colour, result[colour]] for colour in sorted(result)]
