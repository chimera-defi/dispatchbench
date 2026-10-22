from fractions import Fraction
from collections import deque


def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for value in a:
        prefix.append(prefix[-1] + value)

    candidates = deque()
    best_num, best_den = 0, 1

    for end in range(k, len(a) + 1):
        start = end - k

        # Maintain the lower convex hull of eligible prefix points.
        while len(candidates) >= 2:
            x, y = candidates[-2], candidates[-1]
            if (prefix[y] - prefix[x]) * (start - y) >= (
                prefix[start] - prefix[y]
            ) * (y - x):
                candidates.pop()
            else:
                break
        candidates.append(start)

        # The best average ending here is the maximum slope to the hull.
        while len(candidates) >= 2:
            x, y = candidates[0], candidates[1]
            if (prefix[end] - prefix[x]) * (end - y) <= (
                prefix[end] - prefix[y]
            ) * (end - x):
                candidates.popleft()
            else:
                break

        left = candidates[0]
        num = prefix[end] - prefix[left]
        den = end - left
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    divisor = __import__("math").gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
