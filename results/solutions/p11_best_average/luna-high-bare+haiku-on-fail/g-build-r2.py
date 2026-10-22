from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = 0
    best_den = 1

    for right in range(k, n + 1):
        index = right - k
        point = (index, prefix[index])

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (point[1] - y2) - (y2 - y1) * (point[0] - x2) <= 0:
                hull.pop()
            else:
                break
        hull.append(point)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]
            num1 = prefix[right] - y1
            den1 = right - x1
            num2 = prefix[right] - y2
            den2 = right - x2
            if num1 * den2 <= num2 * den1:
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        num = prefix[right] - y
        den = right - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
