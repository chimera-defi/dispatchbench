from fractions import Fraction
from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    # Maintain the lower convex hull of eligible prefix-sum points.
    hull = []
    head = 0
    best_num = 0
    best_den = 1

    for end in range(k, n + 1):
        start = end - k
        point = (start, prefix[start])

        while len(hull) - head >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (y2 - y1) * (start - x2) >= (prefix[start] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(point)

        # Advance the tangent pointer while the next hull point gives a
        # slope to (end, prefix[end]) that is at least as large.
        # slope(p1) <= slope(p2)  <=>  (Ey - y1) * (Ex - x2) <= (Ey - y2) * (Ex - x1)
        while len(hull) - head >= 2:
            x1, y1 = hull[head]
            x2, y2 = hull[head + 1]
            if (prefix[end] - y1) * (end - x2) <= (prefix[end] - y2) * (end - x1):
                head += 1
            else:
                break

        x, y = hull[head]
        num = prefix[end] - y
        den = end - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
