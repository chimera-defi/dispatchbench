def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    compressed = [ranks[value] for value in a]
    size = len(ranks)
    tree = [0] * (size + 1)
    result = [0] * n

    for i, rank in enumerate(compressed):
        if i > k:
            pos = compressed[i - k - 1]
            while pos <= size:
                tree[pos] -= 1
                pos += pos & -pos

        at_most = 0
        pos = rank
        while pos > 0:
            at_most += tree[pos]
            pos -= pos & -pos

        result[i] = min(i, k) - at_most

        pos = rank
        while pos <= size:
            tree[pos] += 1
            pos += pos & -pos

    return result
