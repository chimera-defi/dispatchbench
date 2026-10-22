from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    S = [0] * (n + 1)
    for i, x in enumerate(a):
        S[i + 1] = S[i] + x
    p, q = S[k], k
    g = gcd(p, q)
    p //= g
    q //= g
    while True:
        # prefix sums of a[i]*q - p, computed as S[i]*q - p*i
        best = 0
        bi = bj = -1
        mn = None
        mi = -1
        for j in range(k, n + 1):
            i = j - k
            v = S[i] * q - p * i
            if mn is None or v < mn:
                mn = v
                mi = i
            cur = S[j] * q - p * j - mn
            if cur > best:
                best = cur
                bi, bj = mi, j
        if best <= 0:
            return [p, q]
        p = S[bj] - S[bi]
        q = bj - bi
        g = gcd(p, q)
        p //= g
        q //= g
