from bisect import bisect_left


def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    vals = sorted(set(a))
    m = len(vals)
    rank = {v: i + 1 for i, v in enumerate(vals)}
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
    size = 0
    for i in range(n):
        # Window for position i is indices [max(0, i - k), i - 1]
        if i >= 1:
            update(rank[a[i - 1]], 1)
            size += 1
        if i - k - 1 >= 0:
            update(rank[a[i - k - 1]], -1)
            size -= 1
        # Elements strictly greater than a[i] = window size - elements <= a[i]
        res[i] = size - query(rank[a[i]])
    return res
