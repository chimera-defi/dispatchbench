from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    A = [0] * (n + 1)
    for i, x in enumerate(a):
        A[i + 1] = A[i] + x
    p, q = A[n], n
    while True:
        # prefix of b[i] = a[i]*q - p, i.e. P[j] = A[j]*q - p*j
        minv = None
        mini = 0
        best = None
        bi = bj = 0
        for j in range(k, n + 1):
            i = j - k
            v = A[i] * q - p * i
            if minv is None or v < minv:
                minv = v
                mini = i
            cur = A[j] * q - p * j - minv
            if best is None or cur > best:
                best = cur
                bi, bj = mini, j
        if best <= 0:
            break
        p, q = A[bj] - A[bi], bj - bi
    g = gcd(p, q)
    return [p // g, q // g]
