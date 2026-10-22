def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

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

    result = []
    for i, height in enumerate(a):
        # The window for position i is indices i-k .. i-1, so the element
        # that just left it is a[i-k-1].
        if i > k:
            add(ranks[a[i - k - 1]], -1)

        # Number of window elements with height <= current height.
        not_taller = prefix_sum(ranks[height])
        window_size = min(i, k)
        result.append(window_size - not_taller)

        add(ranks[height], 1)

    return result
