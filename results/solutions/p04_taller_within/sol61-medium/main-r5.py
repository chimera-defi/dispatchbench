def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    m = len(ranks)
    tree = [0] * (m + 1)
    result = [0] * n

    for i, value in enumerate(a):
        if i > k:
            pos = ranks[a[i - k - 1]]
            while pos <= m:
                tree[pos] -= 1
                pos += pos & -pos

        rank = ranks[value]
        pos = rank
        at_most = 0
        while pos:
            at_most += tree[pos]
            pos -= pos & -pos

        result[i] = min(i, k) - at_most

        pos = rank
        while pos <= m:
            tree[pos] += 1
            pos += pos & -pos

    return result
