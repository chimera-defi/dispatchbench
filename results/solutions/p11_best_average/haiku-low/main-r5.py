from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    # Dinkelbach iteration over exact integer arithmetic.
    # With lambda = p/q, maximize sum(sub) - lambda * len(sub) over subarrays of
    # length >= k. Multiplying by q keeps everything integral:
    # q*sum - p*len = (q*P[j] - p*j) - (q*P[i] - p*i).
    n = len(a)
    P = [0] * (n + 1)
    for i, x in enumerate(a):
        P[i + 1] = P[i] + x

    # Start from the whole array, which is a valid candidate since k <= n.
    p, q = P[n], n

    while True:
        best_val = 0
        best_i = best_j = -1
        min_val = None
        min_idx = -1
        for j in range(k, n + 1):
            # Admit prefix index i = j - k into the running minimum.
            i = j - k
            cur = q * P[i] - p * i
            if min_val is None or cur < min_val:
                min_val = cur
                min_idx = i
            val = (q * P[j] - p * j) - min_val
            if val > best_val:
                best_val = val
                best_i = min_idx
                best_j = j

        if best_val <= 0:
            break

        # Strictly improved average; move to it and repeat.
        p = P[best_j] - P[best_i]
        q = best_j - best_i
        g = gcd(p, q)
        p //= g
        q //= g

    g = gcd(p, q)
    return [p // g, q // g]
