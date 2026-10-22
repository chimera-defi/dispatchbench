def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    # Coordinate-compress values to ranks 1..m for the Fenwick tree.
    sorted_vals = sorted(set(a))
    rank = {v: i + 1 for i, v in enumerate(sorted_vals)}
    m = len(sorted_vals)
    tree = [0] * (m + 1)

    def add(pos: int, delta: int) -> None:
        while pos <= m:
            tree[pos] += delta
            pos += pos & -pos

    def prefix(pos: int) -> int:
        total = 0
        while pos > 0:
            total += tree[pos]
            pos -= pos & -pos
        return total

    result = [0] * n
    window_size = 0  # number of elements currently in the window
    for i in range(n):
        # Window for position i is indices [max(0, i - k), i - 1].
        if i >= 1:
            add(rank[a[i - 1]], 1)
            window_size += 1
        if i - k - 1 >= 0:
            add(rank[a[i - k - 1]], -1)
            window_size -= 1
        # Elements strictly greater than a[i] = window_size - (count <= a[i]).
        result[i] = window_size - prefix(rank[a[i]])
    return result
