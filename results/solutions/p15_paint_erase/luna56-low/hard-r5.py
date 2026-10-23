def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    coords = {1, n + 1}
    for op in ops:
        coords.add(op[1])
        coords.add(op[2] + 1)

    xs = sorted(coords)
    m = len(xs) - 1
    inf = 10**20
    no_lazy = -2

    mn = [-1] * (4 * m)
    sm = [inf] * (4 * m)
    cnt = [0] * (4 * m)
    lazy = [no_lazy] * (4 * m)

    def build(p: int, l: int, r: int) -> None:
        cnt[p] = xs[r + 1] - xs[l]
        if l != r:
            q = (l + r) // 2
            build(p * 2, l, q)
            build(p * 2 + 1, q + 1, r)

    def apply_assign(p: int, length: int, value: int) -> None:
        mn[p] = value
        sm[p] = inf
        cnt[p] = length
        lazy[p] = value

    def apply_chmax(p: int, value: int) -> None:
        if value <= mn[p]:
            return
        mn[p] = value
        if lazy[p] != no_lazy:
            lazy[p] = value

    def push(p: int, l: int, r: int) -> None:
        if l == r:
            return

        q = (l + r) // 2
        a, b = p * 2, p * 2 + 1

        if lazy[p] != no_lazy:
            apply_assign(a, xs[q + 1] - xs[l], lazy[p])
            apply_assign(b, xs[r + 1] - xs[q + 1], lazy[p])
            lazy[p] = no_lazy

        apply_chmax(a, mn[p])
        apply_chmax(b, mn[p])

    def pull(p: int) -> None:
        a, b = p * 2, p * 2 + 1
        mn[p] = min(mn[a], mn[b])
        cnt[p] = 0
        sm[p] = inf

        if mn[a] == mn[p]:
            cnt[p] += cnt[a]
            sm[p] = min(sm[p], sm[a])
        else:
            sm[p] = min(sm[p], mn[a])

        if mn[b] == mn[p]:
            cnt[p] += cnt[b]
            sm[p] = min(sm[p], sm[b])
        else:
            sm[p] = min(sm[p], mn[b])

    def erase(p: int, l: int, r: int, ql: int, qr: int) -> None:
        if qr < l or r < ql:
            return
        if ql <= l and r <= qr:
            apply_assign(p, xs[r + 1] - xs[l], -1)
            return

        push(p, l, r)
        q = (l + r) // 2
        erase(p * 2, l, q, ql, qr)
        erase(p * 2 + 1, q + 1, r, ql, qr)
        pull(p)

    def paint_range(p: int, l: int, r: int, ql: int, qr: int, value: int) -> None:
        if qr < l or r < ql or value <= mn[p]:
            return
        if ql <= l and r <= qr and value < sm[p]:
            apply_chmax(p, value)
            return

        push(p, l, r)
        q = (l + r) // 2
        paint_range(p * 2, l, q, ql, qr, value)
        paint_range(p * 2 + 1, q + 1, r, ql, qr, value)
        pull(p)

    build(1, 0, m - 1)

    for op in ops:
        left = bisect_left(xs, op[1])
        right = bisect_left(xs, op[2] + 1) - 1
        if op[0] == 0:
            erase(1, 0, m - 1, left, right)
        else:
            paint_range(1, 0, m - 1, left, right, op[3])

    result = {}

    def collect(p: int, l: int, r: int) -> None:
        if mn[p] >= 0 and sm[p] == inf:
            result[mn[p]] = result.get(mn[p], 0) + cnt[p]
            return

        push(p, l, r)
        if l == r:
            if mn[p] >= 0:
                result[mn[p]] = result.get(mn[p], 0) + cnt[p]
            return

        q = (l + r) // 2
        collect(p * 2, l, q)
        collect(p * 2 + 1, q + 1, r)

    collect(1, 0, m - 1)
    return [[colour, result[colour]] for colour in sorted(result)]
