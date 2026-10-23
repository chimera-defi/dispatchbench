def taller_within(a: list[int], k: int) -> list[int]:
    values = {x: i + 1 for i, x in enumerate(sorted(set(a)))}
    size = len(values)
    bit = [0] * (size + 1)

    def update(index: int, delta: int) -> None:
        while index <= size:
            bit[index] += delta
            index += index & -index

    def prefix(index: int) -> int:
        total = 0
        while index:
            total += bit[index]
            index -= index & -index
        return total

    result = []
    window_size = 0

    for i, height in enumerate(a):
        rank = values[height]
        result.append(window_size - prefix(rank))

        update(rank, 1)
        window_size += 1

        if i >= k:
            update(values[a[i - k]], -1)
            window_size -= 1

    return result
