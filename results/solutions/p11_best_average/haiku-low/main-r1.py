from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, x in enumerate(a):
        prefix[i + 1] = prefix[i] + x

    # Dinkelbach's method with exact integer arithmetic.
    # The current ratio is p/q. Find the subarray maximizing
    # q*sum - p*len over length >= k. If that maximum is positive,
    # its average is strictly larger, so move to it and repeat.
    p, q = prefix[n], n
    while True:
        best = None
        best_i = best_j = -1
        min_val = None
        min_i = -1
        for j in range(k, n + 1):
            i = j - k
            v = q * prefix[i] - p * i
            if min_val is None or v < min_val:
                min_val = v
                min_i = i
            w = (q * prefix[j] - p * j) - min_val
            if best is None or w > best:
                best = w
                best_i = min_i
                best_j = j
        if best <= 0:
            break
        p = prefix[best_j] - prefix[best_i]
        q = best_j - best_i

    g = gcd(p, q)
    return [p // g, q // g]
