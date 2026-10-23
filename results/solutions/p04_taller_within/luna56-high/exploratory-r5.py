def taller_within(a: list[int], k: int) -> list[int]:
    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    size = len(ranks)
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
    active = 0

    for i, height in enumerate(a):
        old = i - k - 1
        if old >= 0:
            update(ranks[a[old]], -1)
            active -= 1

        rank = ranks[height]
        result.append(active - prefix_sum(rank))

        update(rank, 1)
        active += 1

    return result
