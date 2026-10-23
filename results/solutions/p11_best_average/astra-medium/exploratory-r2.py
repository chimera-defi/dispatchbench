from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_p, best_q = 0, 1

    for r in range(k, n + 1):
        j = r - k

        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            if ((prefix[y] - prefix[x]) * (j - y)
                    >= (prefix[j] - prefix[y]) * (y - x)):
                hull.pop()
            else:
                break
        hull.append(j)

        total = prefix[r]
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x, y = hull[mid], hull[mid + 1]
            if ((total - prefix[x]) * (r - y)
                    <= (total - prefix[y]) * (r - x)):
                lo = mid + 1
            else:
                hi = mid

        start = hull[lo]
        p, q = total - prefix[start], r - start
        if p * best_q > best_p * q:
            best_p, best_q = p, q

    divisor = gcd(best_p, best_q)
    return [best_p // divisor, best_q // divisor]
