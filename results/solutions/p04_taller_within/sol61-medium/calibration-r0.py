def taller_within(a: list[int], k: int) -> list[int]:
    if k == 0:
        return [0] * len(a)

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    size = len(ranks)
    tree = [0] * (size + 1)
    result = []

    for i, value in enumerate(a):
        rank = ranks[value]

        count_le = 0
        pos = rank
        while pos:
            count_le += tree[pos]
            pos -= pos & -pos

        result.append(min(i, k) - count_le)

        pos = rank
        while pos <= size:
            tree[pos] += 1
            pos += pos & -pos

        if i >= k:
            pos = ranks[a[i - k]]
            while pos <= size:
                tree[pos] -= 1
                pos += pos & -pos

    return result
