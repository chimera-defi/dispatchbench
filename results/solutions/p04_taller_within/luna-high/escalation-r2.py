def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)

    def add(index: int, delta: int) -> None:
        while index < len(tree):
            tree[index] += delta
            index += index & -index

    def prefix(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    result = []
    window_size = 0

    for i, height in enumerate(a):
        if i > 0:
            add(rank[a[i - 1]], 1)
            window_size += 1

        if i > k:
            add(rank[a[i - k - 1]], -1)
            window_size -= 1

        result.append(window_size - prefix(rank[height]))

    return result
