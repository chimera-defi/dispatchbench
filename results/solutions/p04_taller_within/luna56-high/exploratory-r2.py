def taller_within(a: list[int], k: int) -> list[int]:
    values = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
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
    for i, value in enumerate(a):
        if i - k - 1 >= 0:
            update(values[a[i - k - 1]], -1)

        rank = values[value]
        result.append(i - prefix(rank))
        update(rank, 1)

    return result
