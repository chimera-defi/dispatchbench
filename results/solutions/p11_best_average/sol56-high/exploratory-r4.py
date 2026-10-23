from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    hull: list[int] = []
    best_num = 0
    best_den = 1

    for right in range(k, n + 1):
        new = right - k

        while len(hull) >= 2:
            x1, x2 = hull[-2], hull[-1]
            cross = (
                (x2 - x1) * (prefix[new] - prefix[x1])
                - (prefix[x2] - prefix[x1]) * (new - x1)
            )
            if cross > 0:
                break
            hull.pop()

        hull.append(new)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            left = hull[mid]
            nxt = hull[mid + 1]

            left_num = prefix[right] - prefix[left]
            left_den = right - left
            next_num = prefix[right] - prefix[nxt]
            next_den = right - nxt

            if left_num * next_den <= next_num * left_den:
                lo = mid + 1
            else:
                hi = mid

        left = hull[lo]
        num = prefix[right] - prefix[left]
        den = right - left

        if num * best_den > best_num * den:
            best_num, best_den = num, den

    common = gcd(best_num, best_den)
    return [best_num // common, best_den // common]
