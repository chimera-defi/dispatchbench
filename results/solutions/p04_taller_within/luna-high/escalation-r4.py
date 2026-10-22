def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)

    def add(index: int, delta: int) -> None:
        while index < len(tree):
            tree[index] += delta
            index += index & -index

    def prefix(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    counts = []
    for i, height in enumerate(a):
        expired = i - k - 1
        if expired >= 0:
            add(ranks[a[expired]], -1)

        rank = ranks[height]
        counts.append(min(i, k) - prefix(rank))
        add(rank, 1)

    return counts
