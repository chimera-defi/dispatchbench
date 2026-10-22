from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num, best_den = 0, 1

    for end in range(k, n + 1):
        start = end - k

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (prefix[start] - y2) - (y2 - y1) * (start - x2) <= 0:
                hull.pop()
            else:
                break
        hull.append((start, prefix[start]))

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]
            if (prefix[end] - y1) * (end - x2) <= (prefix[end] - y2) * (end - x1):
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        num, den = prefix[end] - y, end - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
