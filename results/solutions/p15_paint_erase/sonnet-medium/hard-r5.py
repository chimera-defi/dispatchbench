def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    pts = set()
    for op in ops:
        pts.add(op[1])
        pts.add(op[2] + 1)
    points = sorted(pts)
    idx = {p: i for i, p in enumerate(points)}
    m = len(points) - 1
    if m <= 0:
        return []
    size = 1
    log = 0
    while size < m:
        size *= 2
        log += 1
    R = [False] * (2 * size)
    V = [0] * (2 * size)

    def apply(node, reset, v):
        if reset:
            R[node] = True
            V[node] = v
        elif V[node] < v:
            V[node] = v

    def push(p):
        if R[p] or V[p]:
            r = R[p]
            v = V[p]
            apply(2 * p, r, v)
            apply(2 * p + 1, r, v)
            R[p] = False
            V[p] = 0

    for op in ops:
        a = idx[op[1]]
        b = idx[op[2] + 1]
        if op[0] == 0:
            reset, v = True, 0
        else:
            reset, v = False, op[3]
        lo = a + size
        hi = b + size
        for i in range(log, 0, -1):
            if ((lo >> i) << i) != lo:
                push(lo >> i)
            if ((hi >> i) << i) != hi:
                push((hi - 1) >> i)
        l, h = lo, hi
        while l < h:
            if l & 1:
                apply(l, reset, v)
                l += 1
            if h & 1:
                h -= 1
                apply(h, reset, v)
            l >>= 1
            h >>= 1

    for p in range(1, size):
        push(p)

    cnt = {}
    for i in range(m):
        c = V[size + i]
        if c > 0:
            cnt[c] = cnt.get(c, 0) + points[i + 1] - points[i]
    return [[c, cnt[c]] for c in sorted(cnt)]
