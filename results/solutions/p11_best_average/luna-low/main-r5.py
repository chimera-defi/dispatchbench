from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for x in a:
        prefix.append(prefix[-1] + x)

    # For each end index j, maximize (prefix[j] - prefix[i]) / (j - i)
    # over eligible starts i <= j-k. Maintain their lower convex hull.
    hull = []
    head = 0
    best_num, best_den = 0, 1

    for j in range(k, len(a) + 1):
        i = j - k

        while len(hull) - head >= 2:
            x, y = hull[-2], hull[-1]
            # Remove y when x, y, i are not a counterclockwise turn.
            if (prefix[y] - prefix[x]) * (i - y) >= (prefix[i] - prefix[y]) * (y - x):
                hull.pop()
            else:
                break
        hull.append(i)

        while len(hull) - head >= 2:
            x, y = hull[head], hull[head + 1]
            if (prefix[j] - prefix[x]) * (j - y) <= (prefix[j] - prefix[y]) * (j - x):
                head += 1
            else:
                break

        start = hull[head]
        num = prefix[j] - prefix[start]
        den = j - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    f = Fraction(best_num, best_den)
    return [f.numerator, f.denominator]
