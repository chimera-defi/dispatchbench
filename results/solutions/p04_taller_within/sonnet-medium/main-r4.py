from bisect import bisect_left


def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
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
    size = 0
    for i in range(n):
        j = i - k - 1
        if j >= 0:
            update(rank[j], -1)
            size -= 1
        res[i] = size - query(rank[i])
        update(rank[i], 1)
        size += 1
    return res
