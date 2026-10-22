def taller_within(a: list[int], k: int) -> list[int]:
    from bisect import bisect_left, bisect_right

    if k == 0:
        return [0] * len(a)

    values = sorted(set(a))
    size = len(values)
    tree = [0] * (size + 1)

    def add(index: int, delta: int) -> None:
        index += 1
        while index <= size:
            tree[index] += delta
            index += index & -index

    def prefix_sum(end: int) -> int:
        total = 0
        while end:
            total += tree[end]
            end -= end & -end
        return total

    result = []
    for i, height in enumerate(a):
        if i >= k:
            add(bisect_left(values, a[i - k]), -1)

        rank = bisect_right(values, height)
        result.append(prefix_sum(size) - prefix_sum(rank))
        add(bisect_left(values, height), 1)

    return result
