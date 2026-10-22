from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    p, q = prefix[n], n

    while True:
        g = [q * prefix[t] - p * t for t in range(n + 1)]
        min_value = None
        min_index = 0
        best_diff = None
        best_pair = (0, k)

        for j in range(k, n + 1):
            i = j - k
            if min_value is None or g[i] < min_value:
                min_value = g[i]
                min_index = i

            diff = g[j] - min_value
            if best_diff is None or diff > best_diff:
                best_diff = diff
                best_pair = (min_index, j)

        if best_diff <= 0:
            divisor = gcd(p, q)
            return [p // divisor, q // divisor]

        i, j = best_pair
        p = prefix[j] - prefix[i]
        q = j - i
