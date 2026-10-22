from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for value in a:
        prefix.append(prefix[-1] + value)

    hull = []
    best_num, best_den = 0, 1

    for end in range(k, len(a) + 1):
        point = (end - k, prefix[end - k])
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            x3, y3 = point
            if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append(point)

        left, right = 0, len(hull) - 1
        while left < right:
            mid = (left + right) // 2
            x1, y1 = hull[mid]
            x2, y2 = hull[mid + 1]
            num1, den1 = prefix[end] - y1, end - x1
            num2, den2 = prefix[end] - y2, end - x2
            if num1 * den2 < num2 * den1:
                left = mid + 1
            else:
                right = mid

        x, y = hull[left]
        num, den = prefix[end] - y, end - x
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
