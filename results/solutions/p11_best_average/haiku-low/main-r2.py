from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, x in enumerate(a):
        prefix[i + 1] = prefix[i] + x

    # Dinkelbach's method with exact integer arithmetic.
    # For a ratio p/q, a subarray (i, j] has average > p/q iff
    # g[j] - g[i] > 0, where g[t] = q * prefix[t] - p * t.
    p, q = prefix[n], n
    while True:
        g = [q * prefix[t] - p * t for t in range(n + 1)]

        best_diff = 0
        best_i = best_j = -1
        min_val = None
        min_idx = -1
        for j in range(k, n + 1):
            i = j - k
            if min_val is None or g[i] < min_val:
                min_val = g[i]
                min_idx = i
            diff = g[j] - min_val
            if diff > best_diff:
                best_diff = diff
                best_i = min_idx
                best_j = j

        if best_diff <= 0:
            break

        p = prefix[best_j] - prefix[best_i]
        q = best_j - best_i

    d = gcd(p, q)
    return [p // d, q // d]
