from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = best_den = None

    for end in range(k, n + 1):
        start = end - k
        point = (start, prefix[start])

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            cross = (x2 - x1) * (point[1] - y1) - (y2 - y1) * (point[0] - x1)
            if cross <= 0:
                hull.pop()
            else:
                break
        hull.append(point)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            left = (prefix[end] - y1) * (end - x2)
            right = (prefix[end] - y2) * (end - x1)
            if left <= right:
                lo = mid + 1
            else:
                hi = mid

        start, start_sum = hull[lo]
        num = prefix[end] - start_sum
        den = end - start

        if best_num is None or num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
