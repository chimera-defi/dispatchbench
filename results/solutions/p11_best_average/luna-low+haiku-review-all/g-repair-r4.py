from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each right endpoint, the best eligible start is the lower
    # convex hull of prefix-sum points with indices at most right - k.
    hull = []
    head = 0
    best_num, best_den = 0, 1

    for right in range(k, n + 1):
        start = right - k
        while len(hull) - head >= 2:
            x1, y1 = hull[-2], prefix[hull[-2]]
            x2, y2 = hull[-1], prefix[hull[-1]]
            if (y2 - y1) * (start - x2) >= (prefix[start] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(start)

        # Advance head while the next hull point gives a slope to
        # (right, prefix[right]) that is at least as large.
        while len(hull) - head >= 2:
            x1, y1 = hull[head], prefix[hull[head]]
            x2, y2 = hull[head + 1], prefix[hull[head + 1]]
            if (prefix[right] - y1) * (right - x2) <= (prefix[right] - y2) * (right - x1):
                head += 1
            else:
                break

        begin = hull[head]
        numerator = prefix[right] - prefix[begin]
        denominator = right - begin
        if numerator * best_den > best_num * denominator:
            best_num, best_den = numerator, denominator

    fraction = Fraction(best_num, best_den)
    return [fraction.numerator, fraction.denominator]
