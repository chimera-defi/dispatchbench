def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)

    def update(p: int, d: int) -> None:
        while p <= m:
            tree[p] += d
            p += p & -p

    def prefix(p: int) -> int:
        s = 0
        while p > 0:
            s += tree[p]
            p -= p & -p
        return s

    res = [0] * n
    total = 0  # number of elements currently in the window
    for i in range(n):
        # Window for i is [i - k, i - 1]. Add a[i-1] first, then drop a[i-k-1].
        if i >= 1:
            update(rank[a[i - 1]], 1)
            total += 1
        j = i - k - 1
        if j >= 0:
            update(rank[a[j]], -1)
            total -= 1
        # Elements strictly greater than a[i] = total - (count <= a[i])
        res[i] = total - prefix(rank[a[i]])
    return res
