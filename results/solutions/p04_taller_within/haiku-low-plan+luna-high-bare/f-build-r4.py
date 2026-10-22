def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    bit = [0] * (len(values) + 1)

    def add(index: int, delta: int) -> None:
        while index < len(bit):
            bit[index] += delta
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += bit[index]
            index -= index & -index
        return total

    result = []
    size = 0

    for i, height in enumerate(a):
        leaving = i - k - 1
        if leaving >= 0:
            add(ranks[a[leaving]], -1)
            size -= 1

        rank = ranks[height]
        result.append(size - prefix_sum(rank))

        add(rank, 1)
        size += 1

    return result
