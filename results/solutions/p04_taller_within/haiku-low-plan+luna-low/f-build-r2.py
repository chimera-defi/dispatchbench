def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    ranks = [rank[value] for value in a]

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

    for i in range(n):
        if i > 0:
            add(ranks[i - 1], 1)
            size += 1

            expired = i - 1 - k
            if expired >= 0:
                add(ranks[expired], -1)
                size -= 1

        result.append(size - prefix_sum(ranks[i]))

    return result
