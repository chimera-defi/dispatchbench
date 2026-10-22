def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    n = len(a)
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

    answer = [0] * n
    size = 0

    for i in range(n):
        if i >= 1:
            update(ranks[a[i - 1]], 1)
            size += 1

        if i - 1 - k >= 0:
            update(ranks[a[i - 1 - k]], -1)
            size -= 1

        answer[i] = size - prefix_sum(ranks[a[i]])

    return answer
