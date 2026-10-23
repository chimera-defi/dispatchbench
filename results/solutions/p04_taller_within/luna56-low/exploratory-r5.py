def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    m = len(values)
    bit = [0] * (m + 1)

    def add(index: int, delta: int) -> None:
        while index <= m:
            bit[index] += delta
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += bit[index]
            index -= index & -index
        return total

    result = [0] * n
    active = 0

    for i, height in enumerate(a):
        if i > k:
            add(rank[a[i - k - 1]], -1)
            active -= 1

        result[i] = active - prefix_sum(rank[height])
        add(rank[height], 1)
        active += 1

    return result
