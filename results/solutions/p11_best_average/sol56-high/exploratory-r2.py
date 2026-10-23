from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    hull: list[tuple[int, int]] = []
    best_num = -1
    best_den = 1

    for right in range(k, n + 1):
        x = right - k
        y = prefix[x]

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (y - y1) <= (y2 - y1) * (x - x1):
                hull.pop()
            else:
                break
        hull.append((x, y))

        total = prefix[right]
        lo, hi = 0, len(hull) - 1

        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            if (total - y1) * (right - x2) <= (total - y2) * (right - x1):
                lo = mid + 1
            else:
                hi = mid

        left, left_sum = hull[lo]
        numerator = total - left_sum
        denominator = right - left

        if numerator * best_den > best_num * denominator:
            best_num = numerator
            best_den = denominator

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
