from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each right endpoint, find the minimum-slope eligible prefix point.
    # The convex hull supports this in amortized O(1).
    hull = []
    best_num, best_den = 0, 1

    for end in range(k, n + 1):
        new_start = end - k

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            # Remove the middle point when slopes stop increasing.
            if (y2 - y1) * (new_start - x2) >= (prefix[new_start] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((new_start, prefix[new_start]))

        x, y = end, prefix[end]
        while len(hull) >= 2:
            x1, y1 = hull[0]
            x2, y2 = hull[1]
            if (y - y1) * (x2 - x1) >= (y - y2) * (x2 - x1) + (y2 - y1) * (x2 - x1):
                hull.pop(0)
            else:
                break

        start, base = hull[0]
        num, den = y - base, x - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    result = Fraction(best_num, best_den)
    return [result.numerator, result.denominator]
