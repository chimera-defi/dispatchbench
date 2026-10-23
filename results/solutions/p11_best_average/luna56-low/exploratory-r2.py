from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)

    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = -1
    best_den = 1

    for j in range(k, n + 1):
        i = j - k

        while len(hull) >= 2:
            x0, y0 = hull[-2]
            x1, y1 = hull[-1]
            x2, y2 = i, prefix[i]

            cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
            if cross <= 0:
                hull.pop()
            else:
                break

        hull.append((i, prefix[i]))

        left, right = 0, len(hull) - 1
        x, y = j, prefix[j]

        while left < right:
            mid = (left + right) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]

            s1_num = y - y1
            s1_den = x - x1
            s2_num = y - y2
            s2_den = x - x2

            if s1_num * s2_den < s2_num * s1_den:
                left = mid + 1
            else:
                right = mid

        start_x, start_y = hull[left]
        num = y - start_y
        den = x - start_x

        if num * best_den > best_num * den:
            best_num = num
            best_den = den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
