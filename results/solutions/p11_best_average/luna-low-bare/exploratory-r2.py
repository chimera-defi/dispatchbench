from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

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
            if (y2 - y1) * (point[0] - x2) >= (point[1] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(point)

        while len(hull) - head >= 2:
            x1, y1 = hull[head]
            x2, y2 = hull[head + 1]
            if (prefix[end] - y1) * (x2 - x1) <= (prefix[end] - y2) * (x2 - x1):
                head += 1
            else:
                break

        x, y = hull[head]
        num = prefix[end] - y
        den = end - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    result = Fraction(best_num, best_den)
    return [result.numerator, result.denominator]
