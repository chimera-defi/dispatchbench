from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)

    total = 0
    for i, value in enumerate(a, 1):
        total += value
        prefix[i] = total

    hull = []
    best_num = 0
    best_den = 1

    for end in range(k, n + 1):
        start = end - k

        while len(hull) >= 2:
            x1, x2, x3 = hull[-2], hull[-1], start
            cross = (
                (x2 - x1) * (prefix[x3] - prefix[x1])
                - (prefix[x2] - prefix[x1]) * (x3 - x1)
            )
            if cross <= 0:
                hull.pop()
            else:
                break

        hull.append(start)

        if len(hull) == 1:
            candidate = hull[0]
        else:
            lo, hi = 0, len(hull) - 2

            while lo < hi:
                mid = (lo + hi) // 2
                x1, x2 = hull[mid], hull[mid + 1]
                orient = (
                    (x2 - x1) * (prefix[end] - prefix[x1])
                    - (prefix[x2] - prefix[x1]) * (end - x1)
                )
                if orient > 0:
                    lo = mid + 1
                else:
                    hi = mid

            candidate = hull[lo]
            if lo + 1 < len(hull):
                other = hull[lo + 1]
                num1 = prefix[end] - prefix[candidate]
                den1 = end - candidate
                num2 = prefix[end] - prefix[other]
                den2 = end - other
                if num2 * den1 > num1 * den2:
                    candidate = other

        num = prefix[end] - prefix[candidate]
        den = end - candidate

        if num * best_den > best_num * den:
            best_num = num
            best_den = den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
