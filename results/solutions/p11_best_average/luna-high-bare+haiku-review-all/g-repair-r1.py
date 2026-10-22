def best_average(a: list[int], k: int) -> list[int]:
    from math import gcd

    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = 0
    best_den = 1

    def cross(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    for j in range(k, n + 1):
        point = (j - k, prefix[j - k])
        while len(hull) >= 2 and cross(hull[-2], hull[-1], point) <= 0:
            hull.pop()
        hull.append(point)

        query = (j, prefix[j])
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            p, q = hull[mid], hull[mid + 1]
            left = (query[1] - p[1]) * (query[0] - q[0])
            right = (query[1] - q[1]) * (query[0] - p[0])
            if left <= right:
                lo = mid + 1
            else:
                hi = mid

        p = hull[lo]
        num = query[1] - p[1]
        den = query[0] - p[0]
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
