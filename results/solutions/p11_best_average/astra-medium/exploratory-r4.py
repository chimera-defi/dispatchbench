from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num, best_den = 0, 1

    for right in range(k, n + 1):
        new = right - k

        # Maintain the lower convex hull of eligible prefix points.
        while len(hull) >= 2:
            u, v = hull[-2], hull[-1]
            if (
                (v - u) * (prefix[new] - prefix[u])
                > (prefix[v] - prefix[u]) * (new - u)
            ):
                break
            hull.pop()
        hull.append(new)

        # Find the hull point giving the maximum slope to this endpoint.
        total = prefix[right]
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            u, v = hull[mid], hull[mid + 1]
            if (total - prefix[u]) * (right - v) <= (
                total - prefix[v]
            ) * (right - u):
                lo = mid + 1
            else:
                hi = mid

        left = hull[lo]
        numerator = total - prefix[left]
        denominator = right - left
        if numerator * best_den > best_num * denominator:
            best_num, best_den = numerator, denominator

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
