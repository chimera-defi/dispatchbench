from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each right endpoint, the best eligible start is the lower
    # convex hull point maximizing the slope to that endpoint.
    hull = []
    best_num = 0
    best_den = 1

    for end in range(k, n + 1):
        start = end - k
        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            if (prefix[y] - prefix[x]) * (start - y) >= (
                prefix[start] - prefix[y]
            ) * (y - x):
                hull.pop()
            else:
                break
        hull.append(start)

        while len(hull) >= 2:
            x, y = hull[0], hull[1]
            if (prefix[end] - prefix[x]) * (end - y) <= (
                prefix[end] - prefix[y]
            ) * (end - x):
                hull.pop(0)
            else:
                break

        s = hull[0]
        num = prefix[end] - prefix[s]
        den = end - s
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    f = Fraction(best_num, best_den)
    return [f.numerator, f.denominator]
