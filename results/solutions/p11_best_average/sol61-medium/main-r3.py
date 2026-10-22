from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    hull = []
    best_sum, best_len = 0, 1

    for right in range(k, n + 1):
        left = right - k

        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            if ((prefix[y] - prefix[x]) * (left - y)
                    < (prefix[left] - prefix[y]) * (y - x)):
                break
            hull.pop()
        hull.append(left)

        total = prefix[right]
        lo, hi = 0, len(hull) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            x, y = hull[mid], hull[mid + 1]
            if ((total - prefix[x]) * (right - y)
                    <= (total - prefix[y]) * (right - x)):
                lo = mid + 1
            else:
                hi = mid

        start = hull[lo]
        current_sum = total - prefix[start]
        current_len = right - start
        if current_sum * best_len > best_sum * current_len:
            best_sum, best_len = current_sum, current_len

    divisor = gcd(best_sum, best_len)
    return [best_sum // divisor, best_len // divisor]
