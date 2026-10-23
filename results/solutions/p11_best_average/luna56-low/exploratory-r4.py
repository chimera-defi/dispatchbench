def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull: list[int] = []
    best_num = 0
    best_den = 1

    for right in range(k, n + 1):
        point = right - k

        while len(hull) >= 2:
            i, j = hull[-2], hull[-1]
            cross = (
                (j - i) * (prefix[point] - prefix[j])
                - (prefix[j] - prefix[i]) * (point - j)
            )
            if cross <= 0:
                hull.pop()
            else:
                break
        hull.append(point)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            i, j = hull[mid], hull[mid + 1]

            left = (prefix[right] - prefix[i]) * (right - j)
            right_side = (prefix[right] - prefix[j]) * (right - i)

            if left < right_side:
                lo = mid + 1
            else:
                hi = mid

        start = hull[lo]
        num = prefix[right] - prefix[start]
        den = right - start

        if num * best_den > best_num * den:
            best_num, best_den = num, den

    from math import gcd
    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
