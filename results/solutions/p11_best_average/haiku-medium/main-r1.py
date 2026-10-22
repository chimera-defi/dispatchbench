from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    # Start from the whole array, which is always a valid candidate.
    p = sum(a)
    q = n
    while True:
        # Prefix sums of q*a[i] - p. A subarray has average > p/q exactly
        # when its window sum of these terms is positive.
        pref = [0] * (n + 1)
        acc = 0
        for i, x in enumerate(a):
            acc += q * x - p
            pref[i + 1] = acc

        best = 0
        best_i = -1
        best_j = -1
        min_val = None
        min_idx = -1
        for j in range(k, n + 1):
            i = j - k
            if min_val is None or pref[i] < min_val:
                min_val = pref[i]
                min_idx = i
            val = pref[j] - min_val
            if val > best:
                best = val
                best_i = min_idx
                best_j = j

        if best_i < 0:
            break
        p = sum(a[best_i:best_j])
        q = best_j - best_i

    g = gcd(p, q)
    return [p // g, q // g]
