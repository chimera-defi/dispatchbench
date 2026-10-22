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

    n = len(a)
    ans = [0] * n
    size = 0

    for i in range(n):
        if i >= 1:
            add(ranks[a[i - 1]], 1)
            size += 1
        if i - 1 - k >= 0:
            add(ranks[a[i - 1 - k]], -1)
            size -= 1

        ans[i] = size - prefix_sum(ranks[a[i]])

    return ans
