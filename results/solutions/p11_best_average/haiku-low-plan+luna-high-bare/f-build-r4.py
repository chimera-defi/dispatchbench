from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # Lower convex hull of eligible prefix-sum points.
    hull = []
    best_num = 0
    best_den = 1

    for end in range(k, n + 1):
        start = end - k
        point = (start, prefix[start])

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            x3, y3 = point
            if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append(point)

        # Find the hull point giving the largest slope to (end, prefix[end]).
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x0, y0 = hull[mid]
            x1, y1 = hull[mid + 1]
            if (prefix[end] - y0) * (end - x1) < (prefix[end] - y1) * (end - x0):
                lo = mid + 1
            else:
                hi = mid

        start, start_sum = hull[lo]
        num = prefix[end] - start_sum
        den = end - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
