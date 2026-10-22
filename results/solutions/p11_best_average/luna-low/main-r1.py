from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each right endpoint j, maximize
    # (prefix[j] - prefix[i]) / (j - i), with i <= j-k.
    # Maintain the lower convex hull of eligible prefix points (i, prefix[i]).
    hull = []
    head = 0
    best_num = 0
    best_den = 1

    for j in range(k, n + 1):
        i = j - k

        while len(hull) >= head + 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            # Remove x2 when the three points are not a strict lower turn.
            if (x2 - x1) * (prefix[i] - y2) <= (i - x2) * (y2 - y1):
                hull.pop()
            else:
                break
        hull.append((i, prefix[i]))

        xj, yj = j, prefix[j]
        while head + 1 < len(hull):
            x1, y1 = hull[head]
            x2, y2 = hull[head + 1]
            if (yj - y1) * (x2 - x1) <= (yj - y2) * (x2 - x1):
                head += 1
            else:
                break

        xi, yi = hull[head]
        num = yj - yi
        den = xj - xi
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    f = Fraction(best_num, best_den)
    return [f.numerator, f.denominator]
