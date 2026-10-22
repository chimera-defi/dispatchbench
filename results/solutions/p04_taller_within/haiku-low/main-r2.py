def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    # Coordinate-compress values so a Fenwick tree can index them.
    vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)

    def add(p: int, delta: int) -> None:
        while p <= m:
            tree[p] += delta
            p += p & -p

    def prefix(p: int) -> int:
        s = 0
        while p > 0:
            s += tree[p]
            p -= p & -p
        return s

    res = [0] * n
    lo = 0      # window is indices [lo, i) currently inserted in the tree
    size = 0    # number of elements in the window
    for i in range(n):
        if i >= 1:
            add(rank[a[i - 1]], 1)
            size += 1
        # Drop indices that fall outside the k-wide window.
        while lo < i - k:
            add(rank[a[lo]], -1)
            size -= 1
            lo += 1
        # Elements strictly greater than a[i] = size minus those <= a[i].
        res[i] = size - prefix(rank[a[i]])
    return res
