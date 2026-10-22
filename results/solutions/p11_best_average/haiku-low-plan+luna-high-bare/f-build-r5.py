from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    p, q = prefix[n], n

    while True:
        g_values = [q * prefix[t] - p * t for t in range(n + 1)]
        min_g = None
        min_i = 0
        best_diff = None
        best_i = best_j = 0

        for j in range(k, n + 1):
            i = j - k
            if min_g is None or g_values[i] < min_g:
                min_g = g_values[i]
                min_i = i

            diff = g_values[j] - min_g
            if best_diff is None or diff > best_diff:
                best_diff = diff
                best_i, best_j = min_i, j

        if best_diff <= 0:
            divisor = gcd(p, q)
            return [p // divisor, q // divisor]

        p = prefix[best_j] - prefix[best_i]
        q = best_j - best_i
        divisor = gcd(p, q)
        p //= divisor
        q //= divisor
