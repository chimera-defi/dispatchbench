def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = sorted(set(a))
    ranks = {value: i + 1 for i, value in enumerate(values)}
    m = len(values)
    bit = [0] * (m + 1)
    result = [0] * n

    for i, value in enumerate(a):
        if i > k:
            pos = ranks[a[i - k - 1]]
            while pos <= m:
                bit[pos] -= 1
                pos += pos & -pos

        rank = ranks[value]
        pos = rank
        not_taller = 0
        while pos > 0:
            not_taller += bit[pos]
            pos -= pos & -pos

        result[i] = min(i, k) - not_taller

        pos = rank
        while pos <= m:
            bit[pos] += 1
            pos += pos & -pos

    return result
