def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    INF = float('inf')
    pts = set()
    for op in ops:
        pts.add(op[1])
        pts.add(op[2] + 1)
    xs = sorted(pts)
    m = len(xs) - 1  # elementary segments [xs[i], xs[i+1])
    idx = {x: i for i, x in enumerate(xs)}
    size = 1
    while size < m:
        size *= 2
    LO = [0] * (2 * size)
    HI = [INF] * (2 * size)

    def apply(node, lo, hi):
        a, b = LO[node], HI[node]
        a = lo if a < lo else (hi if a > hi else a)
        b = lo if b < lo else (hi if b > hi else b)
        LO[node] = a
        HI[node] = b

    def update(node, nl, nr, ql, qr, lo, hi):
        if qr <= nl or nr <= ql:
            return
        if ql <= nl and nr <= qr:
            apply(node, lo, hi)
            return
        if LO[node] != 0 or HI[node] != INF:
            apply(2 * node, LO[node], HI[node])
            apply(2 * node + 1, LO[node], HI[node])
            LO[node] = 0
            HI[node] = INF
        mid = (nl + nr) // 2
        update(2 * node, nl, mid, ql, qr, lo, hi)
        update(2 * node + 1, mid, nr, ql, qr, lo, hi)

    for op in ops:
        l = idx[op[1]]
        r = idx[op[2] + 1]
        if op[0] == 1:
            update(1, 0, size, l, r, op[3], INF)
        else:
            update(1, 0, size, l, r, 0, 0)

    res = {}
    stack = [1]
    # push down all tags
    for node in range(1, size):
        if LO[node] != 0 or HI[node] != INF:
            apply(2 * node, LO[node], HI[node])
            apply(2 * node + 1, LO[node], HI[node])
            LO[node] = 0
            HI[node] = INF
    for i in range(m):
        node = size + i
        v = LO[node]
        if v > HI[node]:
            v = HI[node]
        if v > 0:
            res[v] = res.get(v, 0) + xs[i + 1] - xs[i]
    return [[c, res[c]] for c in sorted(res)]
