def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    size = len(values)
    bit = [0] * (size + 1)

    def update(index: int, delta: int) -> None:
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
    window_size = 0

    for i, height in enumerate(a):
        rank = ranks[height]
        not_taller = prefix_sum(rank)
        result.append(window_size - not_taller)

        update(rank, 1)
        window_size += 1

        if window_size > k:
            update(ranks[a[i - k]], -1)
            window_size -= 1

    return result
