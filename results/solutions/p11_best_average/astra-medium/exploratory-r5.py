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
            x, y = hull[-2], hull[-1]
            if (
                (prefix[y] - prefix[x]) * (new - y)
                < (prefix[new] - prefix[y]) * (y - x)
            ):
                break
            hull.pop()
        hull.append(new)

        # Slopes to the right endpoint are unimodal on this hull.
        lo, hi = 0, len(hull) - 1
        total = prefix[right]
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
        num = total - prefix[left]
        den = right - left
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
