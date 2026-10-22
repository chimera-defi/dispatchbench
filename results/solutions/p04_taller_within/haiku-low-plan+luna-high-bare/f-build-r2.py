def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
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
        if i > 0:
            add(rank[a[i - 1]], 1)
            size += 1

            expired = i - k - 1
            if expired >= 0:
                add(rank[a[expired]], -1)
                size -= 1

        result.append(size - prefix_sum(rank[height]))

    return result
