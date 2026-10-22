from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    pre = [0] * (n + 1)
    for i, x in enumerate(a):
        pre[i + 1] = pre[i] + x

    # Dinkelbach iteration with exact integer arithmetic.
    # The current guess is p/q. For each end j, find the start i <= j - k
    # minimizing pre[i]*q - i*p. If some subarray has positive value
    # (sum - (p/q)*len > 0), its average is strictly larger, so move to it.
    p, q = pre[n], n
    while True:
        min_val = None
        min_idx = 0
        best_val = None
        best_pair = (0, 0)
        for j in range(k, n + 1):
            i = j - k
            v = pre[i] * q - i * p
            if min_val is None or v < min_val:
                min_val = v
                min_idx = i
            cur = pre[j] * q - j * p - min_val
            if best_val is None or cur > best_val:
                best_val = cur
                best_pair = (min_idx, j)
        if best_val <= 0:
            break
        i, j = best_pair
        p, q = pre[j] - pre[i], j - i

    g = gcd(p, q)
    return [p // g, q // g]
