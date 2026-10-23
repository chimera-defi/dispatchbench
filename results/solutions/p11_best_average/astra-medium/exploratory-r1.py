from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_sum, best_length = 0, 1

    for end in range(k, n + 1):
        start = end - k

        # Maintain the lower convex hull of eligible prefix points.
        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            if ((prefix[y] - prefix[x]) * (start - y)
                    < (prefix[start] - prefix[y]) * (y - x)):
                break
            hull.pop()
        hull.append(start)

        # Find the hull point giving the maximum slope to this endpoint.
        total = prefix[end]
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x, y = hull[mid], hull[mid + 1]
            if ((total - prefix[x]) * (end - y)
                    <= (total - prefix[y]) * (end - x)):
                lo = mid + 1
            else:
                hi = mid

        start = hull[lo]
        current_sum = total - prefix[start]
        current_length = end - start
        if current_sum * best_length > best_sum * current_length:
            best_sum, best_length = current_sum, current_length

    divisor = gcd(best_sum, best_length)
    return [best_sum // divisor, best_length // divisor]
