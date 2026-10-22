def taller_within(a: list[int], k: int) -> list[int]:
    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)

    def add(index: int, delta: int) -> None:
        while index < len(tree):
            tree[index] += delta
            index += index & -index

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    result = []
    active = 0

    for i, height in enumerate(a):
        expired = i - k - 1
        if expired >= 0:
            add(rank[a[expired]], -1)
            active -= 1

        result.append(active - prefix_sum(rank[height]))
        add(rank[height], 1)
        active += 1

    return result
