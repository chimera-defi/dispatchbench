def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)

    def add(i: int, d: int) -> None:
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
    size = 0
    for i in range(n):
        # Window holds a[j] for j in [max(0, i-k), i-1]
        if i >= 1:
            add(rank[a[i - 1]], 1)
            size += 1
        if i - k - 1 >= 0:
            add(rank[a[i - k - 1]], -1)
            size -= 1
        # Count window elements strictly greater than a[i]
        res[i] = size - prefix(rank[a[i]])
    return res
