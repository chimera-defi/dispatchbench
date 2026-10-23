def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    result = [0] * n

    if k == 0:
        return result

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    size = len(values)
    bit = [0] * (size + 1)

    def add(index: int, value: int) -> None:
        while index <= size:
            bit[index] += value
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index > 0:
            total += bit[index]
            index -= index & -index
        return total

    for i, value in enumerate(a):
        left = max(0, i - k)
        rank = ranks[value]
        result[i] = prefix_sum(size) - prefix_sum(rank)
        add(rank, 1)

        if i >= k:
            add(ranks[a[i - k]], -1)

    return result
