from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # Maintain the lower convex hull of eligible prefix points (i, prefix[i]).
    hull = []
    head = 0
    best_num = 0
    best_den = 1

    for end in range(k, n + 1):
        start = end - k
        while len(hull) - head >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            # Remove middle point if the slopes are non-increasing.
            if (y2 - y1) * (start - x2) >= (prefix[start] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((start, prefix[start]))

        # The best slope to this endpoint is from the hull's tangent.
        while len(hull) - head >= 2:
            x1, y1 = hull[head]
            x2, y2 = hull[head + 1]
            if (prefix[end] - y1) * (end - x2) <= (prefix[end] - y2) * (end - x1):
                head += 1
            else:
                break

        x, y = hull[head]
        numerator = prefix[end] - y
        denominator = end - x
        if numerator * best_den > best_num * denominator:
            best_num, best_den = numerator, denominator

    fraction = Fraction(best_num, best_den)
    return [fraction.numerator, fraction.denominator]
