from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    S = [0] * (n + 1)
    for i, x in enumerate(a):
        S[i + 1] = S[i] + x
    p, q = S[k], k
    while True:
        best = 0
        bi = bj = -1
        min_val = None
        min_idx = -1
        for j in range(k, n + 1):
            i = j - k
            v = q * S[i] - p * i
            if min_val is None or v < min_val:
                min_val = v
                min_idx = i
            cand = q * S[j] - p * j - min_val
            if cand > best:
                best = cand
                bi, bj = min_idx, j
        if best <= 0:
            break
        p = S[bj] - S[bi]
        q = bj - bi
    g = gcd(p, q)
    return [p // g, q // g]
