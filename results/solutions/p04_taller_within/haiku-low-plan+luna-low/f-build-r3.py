def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
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
    left = 0

    for i in range(n):
        if i > 0:
            add(ranks[i - 1], 1)

        new_left = max(0, i - k)
        while left < new_left:
            add(ranks[left], -1)
            left += 1

        window_size = i - left
        result.append(window_size - prefix_sum(ranks[i]))

    return result
