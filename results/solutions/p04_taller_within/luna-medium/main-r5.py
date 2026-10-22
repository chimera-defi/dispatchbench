def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

    # Fenwick tree over compressed height ranks.
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

    result = []
    for i, height in enumerate(a):
        rank = ranks[height]
        # Window contains previous positions max(0, i-k) through i-1.
        result.append(min(i, k) - prefix_sum(rank))
        add(rank, 1)

        expired = i - k
        if expired >= 0:
            add(ranks[a[expired]], -1)

    return result
