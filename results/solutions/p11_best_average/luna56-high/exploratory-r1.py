def best_average(a: list[int], k: int) -> list[int]:
    from math import gcd

    n = len(a)
    prefix = [0] * (n + 1)

    total = 0
    for i, value in enumerate(a, 1):
        total += value
        prefix[i] = total

    hull = []
    best_num, best_den = 0, 1

    for right in range(k, n + 1):
        start = right - k

        while len(hull) >= 2:
            x, y, z = hull[-2], hull[-1], start
            if (prefix[y] - prefix[x]) * (z - y) >= (
                prefix[z] - prefix[y]
            ) * (y - x):
                hull.pop()
            else:
                break

        hull.append(start)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            i, j = hull[mid], hull[mid + 1]

            left = (prefix[right] - prefix[i]) * (right - j)
            right_value = (prefix[right] - prefix[j]) * (right - i)

            if left <= right_value:
                lo = mid + 1
            else:
                hi = mid

        start = hull[lo]
        numerator = prefix[right] - prefix[start]
        denominator = right - start

        if numerator * best_den > best_num * denominator:
            best_num, best_den = numerator, denominator

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
