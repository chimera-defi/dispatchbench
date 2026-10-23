def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    result = [0] * n
    if k == 0:
        return result

    ranks = {value: i + 1 for i, value in enumerate(sorted(set(a)))}
    m = len(ranks)
    bit = [0] * (m + 1)

    for i, value in enumerate(a):
        if i > k:
            r = ranks[a[i - k - 1]]
            while r <= m:
                bit[r] -= 1
                r += r & -r

        rank = ranks[value]
        not_taller = 0
        r = rank
        while r > 0:
            not_taller += bit[r]
            r -= r & -r

        result[i] = min(i, k) - not_taller

        r = rank
        while r <= m:
            bit[r] += 1
            r += r & -r

    return result
