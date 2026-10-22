def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    size = len(values)
    tree = [0] * (size + 1)

    def add(index: int, delta: int) -> None:
        while index <= size:
            tree[index] += delta
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    result = [0] * n
    for i, height in enumerate(a):
        if i >= k:
            add(ranks[a[i - k]], -1)
        rank = ranks[height]
        result[i] = i - max(0, i - k) - prefix_sum(rank)
        add(rank, 1)

    return result
