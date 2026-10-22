def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    # Coordinate-compress values to 1..m for a Fenwick tree.
    vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)

    def update(i: int, d: int) -> None:
        while i <= m:
            tree[i] += d
            i += i & -i

    def prefix(i: int) -> int:
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    res = [0] * n
    size = 0  # number of elements currently in the window
    for i in range(n):
        # Window for position i is indices [max(0, i - k), i - 1].
        if i >= 1:
            update(rank[a[i - 1]], 1)
            size += 1
        j = i - k - 1
        if j >= 0:
            update(rank[a[j]], -1)
            size -= 1
        # Elements strictly greater than a[i] = window size - elements <= a[i].
        res[i] = size - prefix(rank[a[i]])
    return res
