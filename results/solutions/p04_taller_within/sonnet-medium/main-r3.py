from bisect import bisect_left

def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n
    vals = sorted(set(a))
    m = len(vals)
    rank = [bisect_left(vals, x) + 1 for x in a]
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
        if i >= 1:
            update(rank[i - 1], 1)
        if i - k - 1 >= 0:
            update(rank[i - k - 1], -1)
        size = min(i, k)
        res[i] = size - query(rank[i])
    return res
