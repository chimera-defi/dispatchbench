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
        while index > 0:
            total += tree[index]
            index -= index & -index
        return total

    result = []
    window_size = 0

    for i, height in enumerate(a):
        rank = ranks[height]
        result.append(window_size - prefix_sum(rank))

        update(rank, 1)
        window_size += 1

        if i >= k:
            update(ranks[a[i - k]], -1)
            window_size -= 1

    return result
