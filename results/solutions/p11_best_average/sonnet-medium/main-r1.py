from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    S = [0] * (n + 1)
    for i, x in enumerate(a):
        S[i + 1] = S[i] + x
    p, q = S[n], n
    while True:
        # P[i] = S[i]*q - p*i ; find max P[j]-P[i] with j-i >= k
        best = 0
        bi = bj = -1
        mn = None
        mni = -1
        for j in range(k, n + 1):
            i = j - k
            v = S[i] * q - p * i
            if mn is None or v < mn:
                mn = v
                mni = i
            d = S[j] * q - p * j - mn
            if d > best:
                best = d
                bi, bj = mni, j
        if best <= 0:
            break
        p, q = S[bj] - S[bi], bj - bi
    g = gcd(p, q)
    return [p // g, q // g]
