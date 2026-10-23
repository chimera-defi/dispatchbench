def best_average(a: list[int], k: int) -> list[int]:
    from math import gcd

    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull: list[int] = []

    def cross(i: int, j: int, t: int) -> int:
        return ((j - i) * (prefix[t] - prefix[i])
                - (prefix[j] - prefix[i]) * (t - i))

    best_num = -1
    best_den = 1

    for right in range(k, n + 1):
        new_left = right - k

        while len(hull) >= 2 and cross(hull[-2], hull[-1], new_left) <= 0:
            hull.pop()
        hull.append(new_left)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            i = hull[mid]
            j = hull[mid + 1]

            left_num = prefix[right] - prefix[i]
            left_den = right - i
            right_num = prefix[right] - prefix[j]
            right_den = right - j

            if left_num * right_den <= right_num * left_den:
                lo = mid + 1
            else:
                hi = mid

        left = hull[lo]
        numerator = prefix[right] - prefix[left]
        denominator = right - left

        if numerator * best_den > best_num * denominator:
            best_num = numerator
            best_den = denominator

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
