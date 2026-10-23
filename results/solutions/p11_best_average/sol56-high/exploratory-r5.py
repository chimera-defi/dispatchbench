from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    hull: list[int] = []
    best_num = -1
    best_den = 1

    def cross(i: int, j: int, m: int) -> int:
        return ((j - i) * (prefix[m] - prefix[i])
                - (prefix[j] - prefix[i]) * (m - i))

    for right in range(k, n + 1):
        candidate = right - k

        while len(hull) >= 2 and cross(hull[-2], hull[-1], candidate) <= 0:
            hull.pop()
        hull.append(candidate)

        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            i = hull[mid]
            j = hull[mid + 1]

            num_i = prefix[right] - prefix[i]
            den_i = right - i
            num_j = prefix[right] - prefix[j]
            den_j = right - j

            if num_i * den_j <= num_j * den_i:
                lo = mid + 1
            else:
                hi = mid

        left = hull[lo]
        num = prefix[right] - prefix[left]
        den = right - left

        if best_num < 0 or num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
