from collections import deque
from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each right endpoint r, maximize (prefix[r] - prefix[l]) / (r - l)
    # over l <= r - k. The lower convex hull of points (l, prefix[l]) supports
    # this query, and the optimal left endpoint only moves right as r grows.
    hull = deque()
    best_num, best_den = 0, 1

    for r in range(k, n + 1):
        l = r - k
        # Add point l to the lower hull, removing points that are not strictly convex.
        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            if (prefix[y] - prefix[x]) * (l - y) >= (prefix[l] - prefix[y]) * (y - x):
                hull.pop()
            else:
                break
        hull.append(l)

        # Drop front points that are no better than their successor for query r.
        while len(hull) >= 2:
            x, y = hull[0], hull[1]
            if (prefix[r] - prefix[x]) * (r - y) <= (prefix[r] - prefix[y]) * (r - x):
                hull.popleft()
            else:
                break

        start = hull[0]
        num = prefix[r] - prefix[start]
        den = r - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    f = Fraction(best_num, best_den)
    return [f.numerator, f.denominator]
