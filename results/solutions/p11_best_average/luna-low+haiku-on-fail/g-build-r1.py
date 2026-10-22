from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each endpoint j, find the minimum prefix[i] / (j - i)
    # over eligible starts i <= j-k. Maintain the lower convex hull
    # of prefix points (i, prefix[i]).
    hull = []
    head = 0
    best_num = 0
    best_den = 1

    for j in range(k, n + 1):
        i = j - k

        while len(hull) - head >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            if (y2 - y1) * (i - x2) >= (prefix[i] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((i, prefix[i]))

        while len(hull) - head >= 2:
            x1, y1 = hull[head]
            x2, y2 = hull[head + 1]
            # Compare slopes from the two hull points to (j, prefix[j]).
            if (prefix[j] - y1) * (j - x2) <= (prefix[j] - y2) * (j - x1):
                head += 1
            else:
                break

        x, y = hull[head]
        num = prefix[j] - y
        den = j - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = __import__("math").gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
