def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    tree = [0] * (len(values) + 1)

    def prefix_sum(index: int) -> int:
        total = 0
        while index:
            total += tree[index]
            index -= index & -index
        return total

    def add(index: int, delta: int) -> None:
        while index < len(tree):
            tree[index] += delta
            index += index & -index

    result = []
    for i, height in enumerate(a):
        if i >= k:
            add(ranks[a[i - k]], -1)

        # Count prior heights <= current; subtract from the window size.
        result.append(min(i, k) - prefix_sum(ranks[height]))
        add(ranks[height], 1)

    return result
