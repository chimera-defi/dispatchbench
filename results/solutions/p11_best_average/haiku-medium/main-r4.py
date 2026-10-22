from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    # Dinkelbach iteration with exact integer arithmetic: for a rational
    # guess p/q, maximize sum(q*a[i] - p) over subarrays of length >= k.
    # A positive maximum means a subarray with average above p/q exists.
    n = len(a)
    p, q = sum(a), n
    while True:
        prefix = [0] * (n + 1)
        s = 0
        for i, x in enumerate(a):
            s += q * x - p
            prefix[i + 1] = s

        best_val = 0
        best_i = best_j = -1
        min_val = 0
        min_idx = -1
        for j in range(k, n + 1):
            i = j - k
            if min_idx < 0 or prefix[i] < min_val:
                min_val = prefix[i]
                min_idx = i
            v = prefix[j] - min_val
            if v > best_val:
                best_val = v
                best_i = min_idx
                best_j = j

        if best_i < 0:
            break
        p = sum(a[best_i:best_j])
        q = best_j - best_i

    g = gcd(p, q)
    return [p // g, q // g]
