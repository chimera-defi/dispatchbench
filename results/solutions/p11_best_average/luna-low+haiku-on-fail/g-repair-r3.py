from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    # Lower convex hull of points (s, prefix[s]) for eligible starts s.
    hull_x = []
    hull_y = []
    best_num = -1
    best_den = 1

    for end in range(k, n + 1):
        start = end - k
        xs = start
        ys = prefix[start]

        # Keep the hull convex: drop the middle point if it lies on or above
        # the segment from its left neighbour to the new point.
        while len(hull_x) >= 2:
            x1, y1 = hull_x[-2], hull_y[-2]
            x2, y2 = hull_x[-1], hull_y[-1]
            if (y2 - y1) * (xs - x2) >= (ys - y2) * (x2 - x1):
                hull_x.pop()
                hull_y.pop()
            else:
                break
        hull_x.append(xs)
        hull_y.append(ys)

        # Find the hull vertex that maximises (prefix[end] - y) / (end - x).
        # Moving from vertex i to i+1 helps iff the edge slope is at most the
        # slope from vertex i+1 to the query point; this predicate is monotone
        # along the hull, so binary search for the switch point.
        qx = end
        qy = prefix[end]
        lo = 0
        hi = len(hull_x) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull_x[mid], hull_y[mid]
            x2, y2 = hull_x[mid + 1], hull_y[mid + 1]
            # slope(v_mid, v_mid+1) <= slope(v_mid+1, query)
            if (y2 - y1) * (qx - x2) <= (qy - y2) * (x2 - x1):
                lo = mid + 1
            else:
                hi = mid

        x, y = hull_x[lo], hull_y[lo]
        num = qy - y
        den = qx - x
        if best_num < 0 or num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
