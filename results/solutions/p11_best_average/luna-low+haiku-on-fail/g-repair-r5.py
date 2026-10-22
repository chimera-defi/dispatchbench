from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, x in enumerate(a):
        prefix[i + 1] = prefix[i] + x

    # Dinkelbach iteration: lambda = p/q is the current best average.
    # For a subarray (l, r] of length >= k, its average exceeds lambda
    # iff q*sum - p*len > 0. Maximize that exactly with integers.
    p, q = prefix[n], n
    while True:
        min_val = None
        min_idx = -1
        best_diff = 0
        best_sum = best_len = 0
        for r in range(k, n + 1):
            l = r - k
            v = q * prefix[l] - p * l
            if min_val is None or v < min_val:
                min_val = v
                min_idx = l
            diff = (q * prefix[r] - p * r) - min_val
            if diff > best_diff:
                best_diff = diff
                best_sum = prefix[r] - prefix[min_idx]
                best_len = r - min_idx
        if best_diff <= 0:
            break
        p, q = best_sum, best_len

    g = gcd(p, q)
    return [p // g, q // g]
