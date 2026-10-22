def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    m = len(ranks)
    bit = [0] * (m + 1)
    result = [0] * n

    for i, value in enumerate(a):
        rank = ranks[value]

        count = 0
        pos = rank
        while pos > 0:
            count += bit[pos]
            pos -= pos & -pos

        result[i] = min(i, k) - count

        pos = rank
        while pos <= m:
            bit[pos] += 1
            pos += pos & -pos

        if i >= k:
            pos = ranks[a[i - k]]
            while pos <= m:
                bit[pos] -= 1
                pos += pos & -pos

    return result
