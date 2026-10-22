from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # Maintain the lower convex hull of eligible prefix-sum points.
    hull = []
    head = 0
    best_num, best_den = 0, 1

    for end in range(k, n + 1):
        start = end - k
        while len(hull) - head >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            x3, y3 = start, prefix[start]
            if (y2 - y1) * (x3 - x2) >= (y3 - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((start, prefix[start]))

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

    divisor = __import__("math").gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
