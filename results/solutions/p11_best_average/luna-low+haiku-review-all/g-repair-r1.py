from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # Lower convex hull of prefix points (i, prefix[i]), built with x increasing.
    # For each endpoint j, the best start is the hull vertex that maximizes
    # the slope to (j, prefix[j]). That slope is unimodal along the hull, so
    # binary search finds it without relying on a monotone front pointer.
    hx = []
    hy = []
    best_num = 0
    best_den = 1

    for j in range(k, n + 1):
        i = j - k
        yi = prefix[i]

        while len(hx) >= 2:
            x1, y1 = hx[-2], hy[-2]
            x2, y2 = hx[-1], hy[-1]
            if (y2 - y1) * (i - x2) >= (yi - y2) * (x2 - x1):
                hx.pop()
                hy.pop()
            else:
                break
        hx.append(i)
        hy.append(yi)

        pj = prefix[j]
        lo, hi = 0, len(hx) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            # slope(mid -> j) <= slope(mid+1 -> j): the optimum is further right.
            if (pj - hy[mid]) * (j - hx[mid + 1]) <= (pj - hy[mid + 1]) * (j - hx[mid]):
                lo = mid + 1
            else:
                hi = mid

        x, y = hx[lo], hy[lo]
        num = pj - y
        den = j - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
