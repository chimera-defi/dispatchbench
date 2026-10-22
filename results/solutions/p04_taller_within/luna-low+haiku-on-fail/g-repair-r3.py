def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)

    def add(index: int, delta: int) -> None:
        while index < len(tree):
            tree[index] += delta
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    counts = []
    for i, height in enumerate(a):
        # Window before position i should hold a[max(0, i-k) .. i-1].
        # Entering step i, drop a[i-k-1] if it is still in the window.
        if i > k:
            add(ranks[a[i - k - 1]], -1)

        window_size = min(i, k)
        rank = ranks[height]
        # Elements in the window that are <= height; the rest are strictly taller.
        counts.append(window_size - prefix_sum(rank))

        add(rank, 1)

    return counts
