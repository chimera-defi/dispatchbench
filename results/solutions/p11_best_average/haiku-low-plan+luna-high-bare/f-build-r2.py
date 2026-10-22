from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_sum = 0
    best_length = 1

    for j in range(k, n + 1):
        i = j - k

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (prefix[i] - y2) - (prefix[i] - y1) * (i - x2) <= 0:
                hull.pop()
            else:
                break
        hull.append((i, prefix[i]))

        def slope_numerator_denominator(pos):
            x, y = hull[pos]
            return prefix[j] - y, j - x

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            num1, den1 = slope_numerator_denominator(mid)
            num2, den2 = slope_numerator_denominator(mid + 1)
            if num1 * den2 <= num2 * den1:
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        sub_sum = prefix[j] - y
        length = j - x
        if sub_sum * best_length > best_sum * length:
            best_sum, best_length = sub_sum, length

    divisor = gcd(best_sum, best_length)
    return [best_sum // divisor, best_length // divisor]
