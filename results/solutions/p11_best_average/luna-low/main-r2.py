from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each end index j, maximize (prefix[j] - prefix[i]) / (j - i)
    # over i <= j-k. This is the slope from point i to point j.
    hull = []
    best_num = 0
    best_den = 1
    have_best = False

    for j in range(k, n + 1):
        i = j - k

        # Add prefix point (i, prefix[i]) to the lower convex hull.
        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (y2 - y1) * (i - x2) >= (prefix[i] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((i, prefix[i]))

        # The best slope to (j, prefix[j]) is a tangent from the hull.
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]
            if (prefix[j] - y1) * (j - x2) <= (prefix[j] - y2) * (j - x1):
                lo = mid + 1
            else:
                hi = mid
        x, y = hull[lo]
        num = prefix[j] - y
        den = j - x

        if not have_best or num * best_den > best_num * den:
            best_num, best_den = num, den
            have_best = True

    fraction = Fraction(best_num, best_den)
    return [fraction.numerator, fraction.denominator]
