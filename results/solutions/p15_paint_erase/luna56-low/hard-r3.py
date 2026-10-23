def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    points = {1, n + 1}
    for op in ops:
        points.add(op[1])
        points.add(op[2] + 1)

    xs = sorted(points)
    m = len(xs) - 1
    lengths = [xs[i + 1] - xs[i] for i in range(m)]

    size = 4 * m + 5
    mx = [0] * size
    sec = [-1] * size
    cnt = [0] * size
    lazy = [-1] * size

    def pull(p):
        a, b = p * 2, p * 2 + 1
        if mx[a] == mx[b]:
            mx[p] = mx[a]
            cnt[p] = cnt[a] + cnt[b]
            sec[p] = max(sec[a], sec[b])
        elif mx[a] > mx[b]:
            mx[p] = mx[a]
            cnt[p] = cnt[a]
            sec[p] = max(sec[a], mx[b])
        else:
            mx[p] = mx[b]
            cnt[p] = cnt[b]
            sec[p] = max(mx[a], sec[b])

    def build(p, l, r):
        if l == r:
            cnt[p] = lengths[l]
            return
        mid = (l + r) // 2
        build(p * 2, l, mid)
        build(p * 2 + 1, mid + 1, r)
        pull(p)

    def apply_zero(p, length):
        mx[p] = 0
        sec[p] = -1
        cnt[p] = length
        lazy[p] = 0

    def apply_chmin(p, value):
        if mx[p] <= value:
            return
        mx[p] = value

    def push(p, l, r):
        if l == r:
            lazy[p] = -1
            return
        a, b = p * 2, p * 2 + 1
        mid = (l + r) // 2

        if lazy[p] == 0:
            apply_zero(a, xs[mid + 1] - xs[l])
            apply_zero(b, xs[r + 1] - xs[mid + 1])
            lazy[p] = -1

        if mx[a] > mx[p]:
            apply_chmin(a, mx[p])
        if mx[b] > mx[p]:
            apply_chmin(b, mx[p])

    def erase(p, l, r, ql, qr):
        if ql <= l and r <= qr:
            apply_zero(p, xs[r + 1] - xs[l])
            return
        push(p, l, r)
        mid = (l + r) // 2
        if ql <= mid:
            erase(p * 2, l, mid, ql, qr)
        if qr > mid:
            erase(p * 2 + 1, mid + 1, r, ql, qr)
        pull(p)

    def limit(p, l, r, ql, qr, value):
        if qr < l or r < ql or mx[p] <= value:
            return
        if ql <= l and r <= qr and sec[p] < value:
            apply_chmin(p, value)
            return
        push(p, l, r)
        mid = (l + r) // 2
        if ql <= mid:
            limit(p * 2, l, mid, ql, qr, value)
        if qr > mid:
            limit(p * 2 + 1, mid + 1, r, ql, qr, value)
        pull(p)

    result = {}

    def collect(p, l, r):
        if mx[p] == 0:
            return
        if l == r:
            result[mx[p]] = result.get(mx[p], 0) + lengths[l]
            return
        push(p, l, r)
        mid = (l + r) // 2
        collect(p * 2, l, mid)
        collect(p * 2 + 1, mid + 1, r)

    build(1, 0, m - 1)

    for op in ops:
        left = bisect_left(xs, op[1])
        right = bisect_left(xs, op[2] + 1) - 1
        if op[0] == 0:
            erase(1, 0, m - 1, left, right)
        else:
            limit(1, 0, m - 1, left, right, op[3])

    collect(1, 0, m - 1)
    return [[color, result[color]] for color in sorted(result)]
