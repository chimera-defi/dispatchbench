from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for value in a:
        prefix.append(prefix[-1] + value)

    hull = []
    best_num, best_den = 0, 1

    for right in range(k, len(a) + 1):
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

        # Find the maximum slope to (right, prefix[right]) exactly.
        total = prefix[right]
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x, y = hull[mid], hull[mid + 1]
            if (total - prefix[x]) * (right - y) <= (
                total - prefix[y]
            ) * (right - x):
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
