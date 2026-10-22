from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # Lower convex hull of eligible prefix-sum points (i, prefix[i]).
    hull = []
    best_num = best_den = 0

    for j in range(k, n + 1):
        i = j - k
        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (prefix[i] - y1) - (y2 - y1) * (i - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append((i, prefix[i]))

        # Slopes from hull points to (j, prefix[j]) are unimodal.
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]
            if (prefix[j] - y1) * (j - x2) <= (prefix[j] - y2) * (j - x1):
                lo = mid + 1
            else:
                hi = mid

        start, start_sum = hull[lo]
        num = prefix[j] - start_sum
        den = j - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
