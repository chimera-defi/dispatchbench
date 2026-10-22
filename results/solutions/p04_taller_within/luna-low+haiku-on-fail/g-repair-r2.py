def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)
    window = 0

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    def add(index: int, delta: int) -> None:
        while index < len(tree):
            tree[index] += delta
            index += index & -index

    result = []
    for i, height in enumerate(a):
        rank = ranks[height]
        result.append(window - prefix_sum(rank))

        add(rank, 1)
        window += 1

        if i - k >= 0:
            add(ranks[a[i - k]], -1)
            window -= 1

    return result
