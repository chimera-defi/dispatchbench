from bisect import bisect_left


def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    vals = sorted(set(a))
    m = len(vals)
    rank = [bisect_left(vals, x) + 1 for x in a]  # 1-based ranks for the Fenwick tree
    tree = [0] * (m + 1)

    def update(i: int, delta: int) -> None:
        while i <= m:
            tree[i] += delta
            i += i & -i

    def query(i: int) -> int:
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    res = [0] * n
    size = 0  # number of elements currently in the window
    for i in range(n):
        if i >= 1:
            update(rank[i - 1], 1)
            size += 1
        j = i - k - 1
        if j >= 0:
            update(rank[j], -1)
            size -= 1
        # Window holds indices [i-k, i-1]; count those strictly greater than a[i].
        res[i] = size - query(rank[i])
    return res
