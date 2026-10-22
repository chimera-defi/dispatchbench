from fractions import Fraction


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    # For each right endpoint, find the minimum-slope eligible prefix point.
    # Maintain the lower convex hull of prefix points (i, prefix[i]).
    hull = []
    head = 0
    best_num, best_den = 0, 1

    for right in range(k, n + 1):
        idx = right - k
        while len(hull) - head >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            # Remove middle point when the three points are not a convex turn.
            if (y2 - y1) * (idx - x2) >= (prefix[idx] - y2) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append((idx, prefix[idx]))

        while len(hull) - head >= 2:
            x1, y1 = hull[head]
            x2, y2 = hull[head + 1]
            if (prefix[right] - y1) * (right - x2) >= (prefix[right] - y2) * (right - x1):
                head += 1
            else:
                break

        start, start_sum = hull[head]
        num = prefix[right] - start_sum
        den = right - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = __import__("math").gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
