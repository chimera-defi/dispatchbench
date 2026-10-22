def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    pts = set()
    for op in ops:
        pts.add(op[1])
        pts.add(op[2] + 1)
    pts = sorted(pts)
    idx = {p: i for i, p in enumerate(pts)}
    m = len(pts) - 1  # elementary segments [pts[i], pts[i+1])
    if m <= 0:
        return []
    K = [1] * (4 * m)
    A = [0] * (4 * m)

    def apply(node, k, a):
        if k:
            if a > A[node]:
                A[node] = a
        else:
            K[node] = 0
            A[node] = a

    def push(node):
        if K[node] != 1 or A[node] != 0:
            k = K[node]
            a = A[node]
            apply(2 * node, k, a)
            apply(2 * node + 1, k, a)
            K[node] = 1
            A[node] = 0

    def update(node, lo, hi, l, r, k, a):
        if l <= lo and hi <= r:
            apply(node, k, a)
            return
        push(node)
        mid = (lo + hi) >> 1
        if l <= mid:
            update(2 * node, lo, mid, l, r, k, a)
        if r > mid:
            update(2 * node + 1, mid + 1, hi, l, r, k, a)

    for op in ops:
        l = idx[op[1]]
        r = idx[op[2] + 1] - 1
        if op[0] == 1:
            update(1, 0, m - 1, l, r, 1, op[3])
        else:
            update(1, 0, m - 1, l, r, 0, 0)

    cnt = {}
    stack = [(1, 0, m - 1)]
    while stack:
        node, lo, hi = stack.pop()
        if lo == hi:
            v = A[node]
            if v > 0:
                cnt[v] = cnt.get(v, 0) + pts[lo + 1] - pts[lo]
            continue
        push(node)
        mid = (lo + hi) >> 1
        stack.append((2 * node, lo, mid))
        stack.append((2 * node + 1, mid + 1, hi))

    return [[c, cnt[c]] for c in sorted(cnt)]
