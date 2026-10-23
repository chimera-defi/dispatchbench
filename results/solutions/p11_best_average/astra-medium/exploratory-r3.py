from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_p, best_q = 0, 1

    for right in range(k, n + 1):
        start = right - k

        # Maintain the lower convex hull of eligible prefix points.
        while len(hull) >= 2:
            u, v = hull[-2], hull[-1]
            if (
                (prefix[v] - prefix[u]) * (start - v)
                < (prefix[start] - prefix[v]) * (v - u)
            ):
                break
            hull.pop()
        hull.append(start)

        # Find the hull point giving the greatest slope to `right`.
        lo, hi = 0, len(hull) - 1
        total = prefix[right]
        while lo < hi:
            mid = (lo + hi) // 2
            u, v = hull[mid], hull[mid + 1]
            if (
                (total - prefix[u]) * (right - v)
                <= (total - prefix[v]) * (right - u)
            ):
                lo = mid + 1
            else:
                hi = mid

        left = hull[lo]
        p, q = total - prefix[left], right - left
        if p * best_q > best_p * q:
            best_p, best_q = p, q

    divisor = gcd(best_p, best_q)
    return [best_p // divisor, best_q // divisor]
