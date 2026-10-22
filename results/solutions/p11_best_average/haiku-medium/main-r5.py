from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i + 1] = P[i] + x

    # Dinkelbach iteration: keep a current ratio p/q (achieved by a valid subarray)
    # and look for a subarray whose sum(a_i - p/q) is positive.
    p, q = P[n], n
    while True:
        # Integer weights w_i = q*a_i - p, prefix sums W, so the test is exact.
        W = [0] * (n + 1)
        for i in range(n):
            W[i + 1] = W[i] + q * a[i] - p

        min_val = W[0]
        min_idx = 0
        best_val = 0
        best = None
        for j in range(k, n + 1):
            i = j - k
            if W[i] < min_val:
                min_val = W[i]
                min_idx = i
            v = W[j] - min_val
            if v > best_val:
                best_val = v
                best = (min_idx, j)

        if best is None:
            break

        i, j = best
        p = P[j] - P[i]
        q = j - i

    g = gcd(p, q)
    return [p // g, q // g]
