def taller_within(a: list[int], k: int) -> list[int]:
    if k <= 0:
        return [0] * len(a)

    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    size = len(values)
    bit = [0] * (size + 1)

    def add(index: int, delta: int) -> None:
        while index <= size:
            bit[index] += delta
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += bit[index]
            index -= index & -index
        return total

    result = []
    for i, value in enumerate(a):
        left = max(0, i - k)
        if i >= k:
            old_value = a[i - k]
            add(rank[old_value], -1)

        result.append(prefix_sum(size) - prefix_sum(rank[value]))
        add(rank[value], 1)

    return result
