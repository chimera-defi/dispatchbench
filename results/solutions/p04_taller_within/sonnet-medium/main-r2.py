def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    r = [rank[x] for x in a]
    m = len(vals)
    tree = [0] * (m + 1)

    def update(i, d):
        while i <= m:
            tree[i] += d
            i += i & -i

    def query(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    res = [0] * n
    for i in range(n):
        if i > 0:
            update(r[i - 1], 1)
        old = i - 1 - k
        if old >= 0:
            update(r[old], -1)
        size = min(i, k)
        res[i] = size - query(r[i])
    return res
