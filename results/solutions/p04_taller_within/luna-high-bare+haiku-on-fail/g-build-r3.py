def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)

    def update(index: int, delta: int) -> None:
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
        if i > k:
            update(ranks[a[i - k - 1]], -1)

        rank = ranks[height]
        result.append(prefix_sum(len(values)) - prefix_sum(rank))

        update(rank, 1)

    return result
