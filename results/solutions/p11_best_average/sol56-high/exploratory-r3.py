from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    hull: list[int] = []
    best_num = -1
    best_den = 1

    for end in range(k, n + 1):
        start = end - k

        while len(hull) >= 2:
            x, y = hull[-2], hull[-1]
            cross = (
                (y - x) * (prefix[start] - prefix[x])
                - (prefix[y] - prefix[x]) * (start - x)
            )
            if cross > 0:
                break
            hull.pop()
        hull.append(start)

        left, right = 0, len(hull) - 1
        while left < right:
            mid = (left + right) // 2
            x, y = hull[mid], hull[mid + 1]
            cross = (
                (y - x) * (prefix[end] - prefix[x])
                - (prefix[y] - prefix[x]) * (end - x)
            )
            if cross >= 0:
                left = mid + 1
            else:
                right = mid

        start = hull[left]
        numerator = prefix[end] - prefix[start]
        denominator = end - start

        if numerator * best_den > best_num * denominator:
            best_num = numerator
            best_den = denominator

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
