def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    coords = {1, n + 1}
    for op in ops:
        coords.add(op[1])
        coords.add(op[2] + 1)
    xs = sorted(coords)
    m = len(xs) - 1
    INF = 10**19

    mn = [0] * (4 * m + 5)
    smn = [INF] * (4 * m + 5)
    cnt = [0] * (4 * m + 5)
    seglen = [0] * (4 * m + 5)
    zero = [False] * (4 * m + 5)

    def build(i, l, r):
        seglen[i] = xs[r + 1] - xs[l]
        if l == r:
            cnt[i] = seglen[i]
            return
        mid = (l + r) // 2
        build(i * 2, l, mid)
        build(i * 2 + 1, mid + 1, r)
        cnt[i] = seglen[i]

    def apply_zero(i):
        mn[i] = 0
        smn[i] = INF
        cnt[i] = seglen[i]
        zero[i] = True

    def apply_raise(i, value):
        if mn[i] < value:
            mn[i] = value

    def pull(i):
        a, b = i * 2, i * 2 + 1
        if mn[a] < mn[b]:
            mn[i] = mn[a]
            cnt[i] = cnt[a]
            smn[i] = min(smn[a], mn[b])
        elif mn[a] > mn[b]:
            mn[i] = mn[b]
            cnt[i] = cnt[b]
            smn[i] = min(mn[a], smn[b])
        else:
            mn[i] = mn[a]
            cnt[i] = cnt[a] + cnt[b]
            smn[i] = min(smn[a], smn[b])

    def push(i):
        if zero[i]:
            apply_zero(i * 2)
            apply_zero(i * 2 + 1)
            zero[i] = False
        value = mn[i]
        if mn[i * 2] < value:
            apply_raise(i * 2, value)
        if mn[i * 2 + 1] < value:
            apply_raise(i * 2 + 1, value)

    def raise_range(i, l, r, ql, qr, value):
        if qr < l or r < ql or mn[i] >= value:
            return
        if ql <= l and r <= qr and smn[i] > value:
            apply_raise(i, value)
            return
        push(i)
        mid = (l + r) // 2
        raise_range(i * 2, l, mid, ql, qr, value)
        raise_range(i * 2 + 1, mid + 1, r, ql, qr, value)
        pull(i)

    def erase_range(i, l, r, ql, qr):
        if qr < l or r < ql:
            return
        if ql <= l and r <= qr:
            apply_zero(i)
            return
        push(i)
        mid = (l + r) // 2
        erase_range(i * 2, l, mid, ql, qr)
        erase_range(i * 2 + 1, mid + 1, r, ql, qr)
        pull(i)

    build(1, 0, m - 1)

    for op in ops:
        l = bisect_left(xs, op[1])
        r = bisect_left(xs, op[2] + 1) - 1
        if op[0] == 0:
            erase_range(1, 0, m - 1, l, r)
        else:
            raise_range(1, 0, m - 1, l, r, op[3])

    result = {}

    def collect(i, l, r):
        if smn[i] == INF:
            if mn[i] != 0:
                result[mn[i]] = result.get(mn[i], 0) + seglen[i]
            return
        push(i)
        mid = (l + r) // 2
        collect(i * 2, l, mid)
        collect(i * 2 + 1, mid + 1, r)

    collect(1, 0, m - 1)
    return [[color, result[color]] for color in sorted(result)]
