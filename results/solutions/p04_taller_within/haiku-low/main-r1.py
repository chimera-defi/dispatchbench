def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    # Coordinate-compress values to ranks 1..m for a Fenwick tree.
    vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)

    def update(i: int, delta: int) -> None:
        while i <= m:
            tree[i] += delta
            i += i & -i

    def prefix(i: int) -> int:
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & -i
        return s

    result = [0] * n
    size = 0  # number of elements currently in the window
    for i in range(n):
        # Window for position i is indices [max(0, i - k), i - 1].
        if i >= 1:
            update(rank[a[i - 1]], 1)
            size += 1
        if i - k - 1 >= 0:
            update(rank[a[i - k - 1]], -1)
            size -= 1
        # Elements strictly greater than a[i] = size - count(<= a[i]).
        result[i] = size - prefix(rank[a[i]])
    return result
