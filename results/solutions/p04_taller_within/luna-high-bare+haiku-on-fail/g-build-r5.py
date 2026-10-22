def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    bit = [0] * (len(values) + 1)

    def update(index: int, delta: int) -> None:
        while index < len(bit):
            bit[index] += delta
            index += index & -index

    def prefix(index: int) -> int:
        total = 0
        while index:
            total += bit[index]
            index -= index & -index
        return total

    result = [0] * len(a)
    window_size = 0

    for i, height in enumerate(a):
        if i > 0:
            update(ranks[a[i - 1]], 1)
            window_size += 1

        expired = i - k - 1
        if expired >= 0:
            update(ranks[a[expired]], -1)
            window_size -= 1

        result[i] = window_size - prefix(ranks[height])

    return result
