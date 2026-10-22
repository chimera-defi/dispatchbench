from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = 0
    best_den = 1

    for j in range(k, n + 1):
        x = j - k
        y = prefix[x]

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (y - y2) - (y2 - y1) * (x - x2) <= 0:
                hull.pop()
            else:
                break
        hull.append((x, y))

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]
            num1, den1 = prefix[j] - y1, j - x1
            num2, den2 = prefix[j] - y2, j - x2
            if num1 * den2 < num2 * den1:
                lo = mid + 1
            else:
                hi = mid

        x0, y0 = hull[lo]
        num, den = prefix[j] - y0, j - x0
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    common = gcd(best_num, best_den)
    return [best_num // common, best_den // common]
