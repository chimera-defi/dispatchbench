def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for x in a:
        prefix.append(prefix[-1] + x)

    hull = []
    best_num = best_den = None

    for j in range(k, len(prefix)):
        i = j - k
        px, py = i, prefix[i]

        while len(hull) >= 2:
            x1, y1 = hull[-2]
            x2, y2 = hull[-1]
            cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
            if cross <= 0:
                hull.pop()
            else:
                break
        hull.append((px, py))

        qx, qy = j, prefix[j]
        lo, hi = 0, len(hull) - 1

        while lo < hi:
            mid = (lo + hi) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            n1, d1 = qy - y1, qx - x1
            n2, d2 = qy - y2, qx - x2

            if n1 * d2 < n2 * d1:
                lo = mid + 1
            else:
                hi = mid

        x, y = hull[lo]
        num, den = qy - y, qx - x

        if best_num is None or num * best_den > best_num * den:
            best_num, best_den = num, den

    import math
    g = math.gcd(best_num, best_den)
    return [best_num // g, best_den // g]
