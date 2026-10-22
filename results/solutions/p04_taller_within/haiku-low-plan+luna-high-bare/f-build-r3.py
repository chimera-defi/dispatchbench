def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    bit = [0] * (len(values) + 1)

    def add(index: int, delta: int) -> None:
        while index < len(bit):
            bit[index] += delta
            index += index & -index

    def prefix(index: int) -> int:
        total = 0
        while index:
            total += bit[index]
            index -= index & -index
        return total

    result = []
    left = 0

    for i, value in enumerate(a):
        if i:
            add(rank[a[i - 1]], 1)

        lo = max(0, i - k)
        while left < lo:
            add(rank[a[left]], -1)
            left += 1

        window_size = i - lo
        result.append(window_size - prefix(rank[value]))

    return result
