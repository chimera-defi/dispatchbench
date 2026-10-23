def best_average(a: list[int], k: int) -> list[int]:
    import math

    prefix = [0]
    for value in a:
        prefix.append(prefix[-1] + value)

    hull: list[tuple[int, int]] = []
    best_num = 0
    best_den = 1

    for j in range(k, len(prefix)):
        x, y = j - k, prefix[j - k]

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
            if cross <= 0:
                hull.pop()
            else:
                break
        hull.append((x, y))

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            n1, d1 = prefix[j] - y1, j - x1
            n2, d2 = prefix[j] - y2, j - x2

            if n1 * d2 < n2 * d1:
                lo = mid + 1
            else:
                hi = mid

        bx, by = hull[lo]
        num = prefix[j] - by
        den = j - bx

        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = math.gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
