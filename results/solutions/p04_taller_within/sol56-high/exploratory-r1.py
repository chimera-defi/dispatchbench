def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    bit = [0] * (len(values) + 1)

    def update(index: int, delta: int) -> None:
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

    for i, height in enumerate(a):
        expired = i - k - 1
        if expired >= 0:
            update(ranks[a[expired]], -1)

        rank = ranks[height]
        window_size = min(i, k)
        result.append(window_size - prefix_sum(rank))
        update(rank, 1)

    return result
