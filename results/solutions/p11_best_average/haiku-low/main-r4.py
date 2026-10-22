from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    # Start from the whole array, which is always a valid candidate.
    p = sum(a)
    q = n

    while True:
        # Maximize sum of (q*a[i] - p) over subarrays of length >= k.
        # A subarray sum > 0 means its average exceeds p/q.
        best_sum = None
        best_i = best_j = 0

        prefix = 0          # P[j] = sum of b[0..j-1]
        min_prefix = None   # min of P[i] for i <= j - k
        min_idx = 0
        prefix_vals = [0] * (n + 1)
        for t in range(n):
            prefix_vals[t + 1] = prefix_vals[t] + (q * a[t] - p)

        for j in range(k, n + 1):
            i_cand = j - k
            if min_prefix is None or prefix_vals[i_cand] < min_prefix:
                min_prefix = prefix_vals[i_cand]
                min_idx = i_cand
            cur = prefix_vals[j] - min_prefix
            if best_sum is None or cur > best_sum:
                best_sum = cur
                best_i = min_idx
                best_j = j

        if best_sum is None or best_sum <= 0:
            break

        # Move the ratio to the average of the subarray found.
        p = sum(a[best_i:best_j])
        q = best_j - best_i

    g = gcd(p, q)
    return [p // g, q // g]
