def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    m = len(ranks)
    tree = [0] * (m + 1)
    result = [0] * n

    for i, value in enumerate(a):
        rank = ranks[value]

        count_le = 0
        p = rank
        while p > 0:
            count_le += tree[p]
            p -= p & -p

        result[i] = min(i, k) - count_le

        p = rank
        while p <= m:
            tree[p] += 1
            p += p & -p

        if i >= k:
            p = ranks[a[i - k]]
            while p <= m:
                tree[p] -= 1
                p += p & -p

    return result
