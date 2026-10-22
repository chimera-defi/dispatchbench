from math import gcd
from itertools import accumulate


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    S = [0] + list(accumulate(a))
    p, q = S[n], n
    while True:
        # maximize (q*S[j] - p*j) - (q*S[i] - p*i) over j - i >= k
        min_val = None
        min_idx = 0
        best = 0
        bi = bj = -1
        for j in range(k, n + 1):
            i = j - k
            v = q * S[i] - p * i
            if min_val is None or v < min_val:
                min_val = v
                min_idx = i
            cur = q * S[j] - p * j - min_val
            if cur > best:
                best = cur
                bi, bj = min_idx, j
        if best <= 0:
            break
        p, q = S[bj] - S[bi], bj - bi
    g = gcd(p, q)
    return [p // g, q // g]
