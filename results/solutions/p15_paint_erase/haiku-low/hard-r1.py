def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Stored value w = -colour, blank = 0. A paint with colour c becomes
    # chmin(w, -c), which keeps the larger colour and fills blank or smaller ones.
    BLANK = 0
    NEG = -(1 << 62)

    pts = {1, n + 1}
    for op in ops:
        pts.add(op[1])
        pts.add(op[2] + 1)
    pts = sorted(pts)
    idx = {p: i for i, p in enumerate(pts)}
    m = len(pts) - 1
    lengths = [pts[i + 1] - pts[i] for i in range(m)]

    size = 4 * m
    mx = [BLANK] * size   # maximum value in node
    se = [NEG] * size     # strict second maximum in node
    tag = [None] * size   # pending uniform assignment

    def set_all(node, v):
        mx[node] = v
        se[node] = NEG
        tag[node] = v

    def push(node):
        lc, rc = 2 * node, 2 * node + 1
        if tag[node] is not None:
            set_all(lc, tag[node])
            set_all(rc, tag[node])
            tag[node] = None
        for c in (lc, rc):
            if mx[c] > mx[node]:
                mx[c] = mx[node]

    def pull(node):
        a, b = 2 * node, 2 * node + 1
        if mx[a] == mx[b]:
            mx[node] = mx[a]
            se[node] = max(se[a], se[b])
        elif mx[a] > mx[b]:
            mx[node] = mx[a]
            se[node] = max(se[a], mx[b])
        else:
            mx[node] = mx[b]
            se[node] = max(mx[a], se[b])

    def assign(node, lo, hi, l, r, v):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            set_all(node, v)
            return
        push(node)
        mid = (lo + hi) // 2
        assign(2 * node, lo, mid, l, r, v)
        assign(2 * node + 1, mid + 1, hi, l, r, v)
        pull(node)

    def chmin(node, lo, hi, l, r, c):
        if r < lo or hi < l or mx[node] <= c:
            return
        if l <= lo and hi <= r and se[node] < c:
            mx[node] = c
            return
        push(node)
        mid = (lo + hi) // 2
        chmin(2 * node, lo, mid, l, r, c)
        chmin(2 * node + 1, mid + 1, hi, l, r, c)
        pull(node)

    for op in ops:
        if op[0] == 1:
            _, l, r, c = op
            chmin(1, 0, m - 1, idx[l], idx[r + 1] - 1, -c)
        else:
            _, l, r = op
            assign(1, 0, m - 1, idx[l], idx[r + 1] - 1, BLANK)

    res = {}

    def collect(node, lo, hi):
        if lo == hi:
            w = mx[node]
            if w != BLANK:
                res[-w] = res.get(-w, 0) + lengths[lo]
            return
        push(node)
        mid = (lo + hi) // 2
        collect(2 * node, lo, mid)
        collect(2 * node + 1, mid + 1, hi)

    collect(1, 0, m - 1)
    return [[c, res[c]] for c in sorted(res)]
