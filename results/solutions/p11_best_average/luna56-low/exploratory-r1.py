def best_average(a: list[int], k: int) -> list[int]:
    from math import gcd

    n = len(a)
    prefix = [0] * (n + 1)
    for i, x in enumerate(a):
        prefix[i + 1] = prefix[i] + x

    hull = []
    best_num = best_den = None

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    for j in range(k, n + 1):
        point = (j - k, prefix[j - k])
        while len(hull) >= 2 and cross(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)

        qx, qy = j, prefix[j]

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            left = (qy - y1) * (qx - x2)
            right = (qy - y2) * (qx - x1)

            if left <= right:
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        num = qy - y
        den = qx - x

        if best_num is None or num * best_den > best_num * den:
            best_num, best_den = num, den

    g = gcd(best_num, best_den)
    return [best_num // g, best_den // g]
