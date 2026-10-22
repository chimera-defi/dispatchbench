from fractions import Fraction
from collections import deque


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    candidates = deque()
    best_num = 0
    best_den = 1

    for end in range(k, n + 1):
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

        # The maximum slope from the hull to this endpoint.
        while len(candidates) >= 2:
            x, y = candidates[0], candidates[1]
            if (prefix[end] - prefix[x]) * (y - x) <= (
                prefix[end] - prefix[y]
            ) * (end - y):
                candidates.popleft()
            else:
                break

        start = candidates[0]
        num = prefix[end] - prefix[start]
        den = end - start
        if num * best_den > best_num * den:
            best_num, best_den = num, den

    fraction = Fraction(best_num, best_den)
    return [fraction.numerator, fraction.denominator]
