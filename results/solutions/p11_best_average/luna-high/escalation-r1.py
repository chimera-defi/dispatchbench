from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for value in a:
        prefix.append(prefix[-1] + value)

    hull = []
    best_num = 0
    best_den = 1

    for end in range(k, len(a) + 1):
        start = end - k
        point = (start, prefix[start])

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
            num1 = prefix[end] - y1
            den1 = end - x1
            num2 = prefix[end] - y2
            den2 = end - x2

            if num1 * den2 <= num2 * den1:
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        num = prefix[end] - y
        den = end - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
