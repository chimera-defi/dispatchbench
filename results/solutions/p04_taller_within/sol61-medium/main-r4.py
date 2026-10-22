def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    m = len(ranks)
    bit = [0] * (m + 1)
    result = [0] * n

    for i, value in enumerate(a):
        if i > k:
            pos = ranks[a[i - k - 1]]
            while pos <= m:
                bit[pos] -= 1
                pos += pos & -pos

        rank = ranks[value]
        count_le = 0
        pos = rank
        while pos:
            count_le += bit[pos]
            pos -= pos & -pos

        result[i] = min(i, k) - count_le

        pos = rank
        while pos <= m:
            bit[pos] += 1
            pos += pos & -pos

    return result
