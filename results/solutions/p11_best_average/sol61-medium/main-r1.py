from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_p, best_q = 0, 1

    for right in range(k, n + 1):
        new = right - k

        # Maintain the lower convex hull of eligible prefix points.
        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            if (
                (y - x) * (prefix[new] - prefix[x])
                > (prefix[y] - prefix[x]) * (new - x)
            ):
                break
            hull.pop()
        hull.append(new)

        # Slopes to the current endpoint are unimodal along the hull.
        total = prefix[right]
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x, y = hull[mid], hull[mid + 1]
            if (
                (total - prefix[x]) * (right - y)
                <= (total - prefix[y]) * (right - x)
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
