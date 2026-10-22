from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    p, q = prefix[n], n

    while True:
        best_value = None
        best_i = best_j = 0
        min_g = None
        min_i = 0

        for j in range(k, n + 1):
            i = j - k
            g_value = q * prefix[i] - p * i
            if min_g is None or g_value < min_g:
                min_g = g_value
                min_i = i

            value = q * prefix[j] - p * j - min_g
            if best_value is None or value > best_value:
                best_value = value
                best_i, best_j = min_i, j

        if best_value <= 0:
            divisor = gcd(p, q)
            return [p // divisor, q // divisor]

        p = prefix[best_j] - prefix[best_i]
        q = best_j - best_i
