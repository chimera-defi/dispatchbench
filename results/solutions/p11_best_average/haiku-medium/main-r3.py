from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i + 1] = P[i] + x

    # Dinkelbach iteration on the exact fraction p/q (starts from a feasible subarray).
    p, q = P[k], k
    while True:
        best = 0
        bi = bj = -1
        mn = None
        mi = -1
        for j in range(k, n + 1):
            i = j - k
            v = q * P[i] - p * i
            if mn is None or v < mn:
                mn = v
                mi = i
            val = (q * P[j] - p * j) - mn
            if val > best:
                best = val
                bi = mi
                bj = j
        if best <= 0:
            break
        p = P[bj] - P[bi]
        q = bj - bi

    g = gcd(p, q)
    return [p // g, q // g]
