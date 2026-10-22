from collections import deque
from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    p, q = prefix[n], n

    while True:
        candidates = deque()
        best_value = 0
        best_pair = None

        for r in range(k, n + 1):
            i = r - k
            g_i = q * prefix[i] - p * i
            while candidates and q * prefix[candidates[-1]] - p * candidates[-1] >= g_i:
                candidates.pop()
            candidates.append(i)

            min_start = r - (2 * k - 1)
            while candidates and candidates[0] < min_start:
                candidates.popleft()

            i = candidates[0]
            value = (q * prefix[r] - p * r) - (q * prefix[i] - p * i)
            if value > best_value:
                best_value = value
                best_pair = (i, r)

        if best_pair is None:
            break

        i, r = best_pair
        p = prefix[r] - prefix[i]
        q = r - i

    divisor = gcd(p, q)
    return [p // divisor, q // divisor]
