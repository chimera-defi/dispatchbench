def best_average(a: list[int], k: int) -> list[int]:
    from math import gcd

    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = 0
    best_den = 1

    for r in range(k, n + 1):
        i = r - k
        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (x2 - x1) * (prefix[i] - y1) - (y2 - y1) * (i - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append((i, prefix[i]))

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            i1, y1 = hull[mid]
            i2, y2 = hull[mid + 1]
            num1, den1 = prefix[r] - y1, r - i1
            num2, den2 = prefix[r] - y2, r - i2
            if num1 * den2 <= num2 * den1:
                lo = mid + 1
            else:
                hi = mid

        start, start_sum = hull[lo]
        num, den = prefix[r] - start_sum, r - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
