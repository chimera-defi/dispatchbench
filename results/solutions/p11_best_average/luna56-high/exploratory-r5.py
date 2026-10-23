def best_average(a: list[int], k: int) -> list[int]:
    from math import gcd

    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    hull: list[tuple[int, int]] = []
    best_num = 0
    best_den = 1

    for j in range(k, n + 1):
        i = j - k
        point = (i, prefix[i])

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            x3, y3 = point
            if (x2 - x1) * (y3 - y1) <= (y2 - y1) * (x3 - x1):
                hull.pop()
            else:
                break

        hull.append(point)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            n1 = prefix[j] - y1
            d1 = j - x1
            n2 = prefix[j] - y2
            d2 = j - x2

            if n1 * d2 <= n2 * d1:
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        num = prefix[j] - y
        den = j - x

        if num * best_den > best_num * den:
            best_num = num
            best_den = den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
