from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    p, q = sum(a), n
    g = gcd(p, q)
    p, q = p // g, q // g

    # Dinkelbach iteration: for the current ratio p/q, find a subarray of
    # length >= k maximizing sum(q*a[i] - p). If the maximum is positive,
    # its average exceeds p/q, so adopt it and repeat. Otherwise p/q is optimal.
    # All arithmetic is in exact Python integers.
    while True:
        prefix = [0] * (n + 1)
        for i, x in enumerate(a):
            prefix[i + 1] = prefix[i] + q * x - p

        min_val = prefix[0]
        min_idx = 0
        best_val = 0
        bi = bj = -1
        for j in range(k, n + 1):
            cand = j - k
            if prefix[cand] < min_val:
                min_val = prefix[cand]
                min_idx = cand
            v = prefix[j] - min_val
            if v > best_val:
                best_val = v
                bi, bj = min_idx, j

        if bi < 0:
            return [p, q]

        s = sum(a[bi:bj])
        length = bj - bi
        g = gcd(s, length)
        p, q = s // g, length // g
