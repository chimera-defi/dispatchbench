def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = sorted(set(a))
    rank = {value: i + 1 for i, value in enumerate(values)}
    m = len(values)
    bit = [0] * (m + 1)
    result = [0] * n

    for i, value in enumerate(a):
        r = rank[value]

        # Count heights less than or equal to the current height.
        count = 0
        p = r
        while p > 0:
            count += bit[p]
            p -= p & -p

        result[i] = min(i, k) - count

        # Add the current person to the window.
        p = r
        while p <= m:
            bit[p] += 1
            p += p & -p

        # Remove the person outside the next position's window.
        if i >= k:
            p = rank[a[i - k]]
            while p <= m:
                bit[p] -= 1
                p += p & -p

    return result
