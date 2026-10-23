from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)

    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_num = 0
    best_den = 1

    for right in range(k, n + 1):
        left = right - k

        while len(hull) >= 2:
            x1 = hull[-2]
            x2 = hull[-1]
            x3 = left

            cross = (
                (x2 - x1) * (prefix[x3] - prefix[x1])
                - (prefix[x2] - prefix[x1]) * (x3 - x1)
            )

            if cross <= 0:
                hull.pop()
            else:
                break

        hull.append(left)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            i = hull[mid]
            j = hull[mid + 1]

            left_num = prefix[right] - prefix[i]
            left_den = right - i
            right_num = prefix[right] - prefix[j]
            right_den = right - j

            if left_num * right_den < right_num * left_den:
                lo = mid + 1
            else:
                hi = mid

        start = hull[lo]
        num = prefix[right] - prefix[start]
        den = right - start

        if num * best_den > best_num * den:
            best_num = num
            best_den = den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
