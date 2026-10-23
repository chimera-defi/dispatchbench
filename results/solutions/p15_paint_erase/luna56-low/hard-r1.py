def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    points = {1, n + 1}
    for op in ops:
        points.add(op[1])
        points.add(op[2] + 1)

    xs = sorted(points)
    m = len(xs) - 1
    inf = 10**30

    mn = [0] * (4 * m)
    sec = [inf] * (4 * m)
    cnt = [0] * (4 * m)
    lazy = [None] * (4 * m)

    def build(p, l, r):
        if l == r:
            cnt[p] = xs[l + 1] - xs[l]
            return
        mid = (l + r) // 2
        build(p * 2, l, mid)
        build(p * 2 + 1, mid + 1, r)
        cnt[p] = cnt[p * 2] + cnt[p * 2 + 1]

    def apply_assign(p, value, length):
        mn[p] = value
        sec[p] = inf
        cnt[p] = length
        lazy[p] = value

    def apply_chmax(p, value):
        if value <= mn[p]:
            return
        mn[p] = value
        if lazy[p] is not None:
            lazy[p] = max(lazy[p], value)

    def pull(p):
        a, b = p * 2, p * 2 + 1
        if mn[a] < mn[b]:
            mn[p] = mn[a]
            cnt[p] = cnt[a]
            sec[p] = min(sec[a], mn[b])
        elif mn[b] < mn[a]:
            mn[p] = mn[b]
            cnt[p] = cnt[b]
            sec[p] = min(mn[a], sec[b])
        else:
            mn[p] = mn[a]
            cnt[p] = cnt[a] + cnt[b]
            sec[p] = min(sec[a], sec[b])

    def push(p, l, r):
        if l == r:
            lazy[p] = None
            return
        a, b = p * 2, p * 2 + 1
        mid = (l + r) // 2

        if lazy[p] is not None:
            value = lazy[p]
            apply_assign(a, value, xs[mid + 1] - xs[l])
            apply_assign(b, value, xs[r + 1] - xs[mid + 1])
            lazy[p] = None

        if mn[a] < mn[p]:
            apply_chmax(a, mn[p])
        if mn[b] < mn[p]:
            apply_chmax(b, mn[p])

    def erase(p, l, r, ql, qr):
        if qr < l or r < ql:
            return
        if ql <= l and r <= qr:
            apply_assign(p, 0, xs[r + 1] - xs[l])
            return
        push(p, l, r)
        mid = (l + r) // 2
        erase(p * 2, l, mid, ql, qr)
        erase(p * 2 + 1, mid + 1, r, ql, qr)
        pull(p)

    def raise_min(p, l, r, ql, qr, value):
        if qr < l or r < ql or value <= mn[p]:
            return
        if ql <= l and r <= qr and value < sec[p]:
            apply_chmax(p, value)
            return
        if l == r:
            apply_chmax(p, value)
            return
        push(p, l, r)
        mid = (l + r) // 2
        raise_min(p * 2, l, mid, ql, qr, value)
        raise_min(p * 2 + 1, mid + 1, r, ql, qr, value)
        pull(p)

    build(1, 0, m - 1)

    for op in ops:
        l = bisect_left(xs, op[1])
        r = bisect_left(xs, op[2] + 1) - 1
        if op[0] == 0:
            erase(1, 0, m - 1, l, r)
        else:
            raise_min(1, 0, m - 1, l, r, op[3])

    result = {}

    def collect(p, l, r):
        if sec[p] == inf:
            if mn[p]:
                result[mn[p]] = result.get(mn[p], 0) + xs[r + 1] - xs[l]
            return
        push(p, l, r)
        mid = (l + r) // 2
        collect(p * 2, l, mid)
        collect(p * 2 + 1, mid + 1, r)

    collect(1, 0, m - 1)
    return [[color, result[color]] for color in sorted(result)]
