def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
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
    total = 0  # number of values currently in the window [i-k, i)
    for i in range(n):
        out = i - k - 1
        if out >= 0:
            update(rank[a[out]], -1)
            total -= 1
        res[i] = total - prefix(rank[a[i]])
        update(rank[a[i]], 1)
        total += 1
    return res
