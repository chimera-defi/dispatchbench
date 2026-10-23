def taller_within(a: list[int], k: int) -> list[int]:
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
    window_size = 0

    for i, height in enumerate(a):
        rank = ranks[height]
        result.append(window_size - prefix_sum(rank))

        add(rank, 1)
        window_size += 1

        if window_size > k:
            add(ranks[a[i - k]], -1)
            window_size -= 1

    return result
