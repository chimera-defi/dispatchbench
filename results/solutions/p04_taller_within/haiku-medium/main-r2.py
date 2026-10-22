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
    for i in range(n):
        # Window for position i is indices [max(0, i - k), i - 1].
        if i >= 1:
            update(rank[a[i - 1]], 1)
        j = i - k - 1
        if j >= 0:
            update(rank[a[j]], -1)
        window_size = min(i, k)
        # Taller = window elements minus those with value <= a[i].
        res[i] = window_size - prefix(rank[a[i]])
    return res
