import sys

def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    sys.setrecursionlimit(10000)
    pts = {1, n + 1}
    for op in ops:
        pts.add(op[1])
        pts.add(op[2] + 1)
    coords = sorted(pts)
    idx = {v: i for i, v in enumerate(coords)}
    k = len(coords) - 1  # elementary segments
    size = 4 * k + 4
    A = [-1] * size
    M = [0] * size

    def apply(node, a, m):
        if a >= 0:
            A[node] = a
            M[node] = m
        elif A[node] >= 0:
            if m > A[node]:
                A[node] = m
        elif m > M[node]:
            M[node] = m

    def push(node):
        a = A[node]
        m = M[node]
        if a >= 0 or m > 0:
            l = node * 2
            r = l + 1
            apply(l, a, m)
            apply(r, a, m)
            A[node] = -1
            M[node] = 0

    def update(node, lo, hi, ql, qr, a, m):
        if ql <= lo and hi <= qr:
            apply(node, a, m)
            return
        push(node)
        mid = (lo + hi) >> 1
        if ql <= mid:
            update(node * 2, lo, mid, ql, qr, a, m)
        if qr > mid:
            update(node * 2 + 1, mid + 1, hi, ql, qr, a, m)

    for op in ops:
        li = idx[op[1]]
        ri = idx[op[2] + 1] - 1
        if op[0] == 1:
            update(1, 0, k - 1, li, ri, -1, op[3])
        else:
            update(1, 0, k - 1, li, ri, 0, 0)

    res = {}

    def collect(node, lo, hi):
        if lo == hi:
            v = A[node] if A[node] >= 0 else M[node]
            if v > 0:
                res[v] = res.get(v, 0) + coords[lo + 1] - coords[lo]
            return
        push(node)
        mid = (lo + hi) >> 1
        collect(node * 2, lo, mid)
        collect(node * 2 + 1, mid + 1, hi)

    collect(1, 0, k - 1)
    return [[c, res[c]] for c in sorted(res)]
