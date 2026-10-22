from fractions import Fraction
from collections import deque

def best_average(a: list[int], k: int) -> list[int]:
    prefix = [0]
    for x in a:
        prefix.append(prefix[-1] + x)

    candidates = deque()
    best = Fraction(-1, 1)

    for end in range(k, len(a) + 1):
        start = end - k
        while len(candidates) >= 2:
            x, y = candidates[-2], candidates[-1]
            if (prefix[y] - prefix[x]) * (start - y) >= (prefix[start] - prefix[y]) * (y - x):
                candidates.pop()
            else:
                break
        candidates.append(start)

        while len(candidates) >= 2:
            x, y = candidates[0], candidates[1]
            if (prefix[y] - prefix[x]) * (end - y) <= (prefix[end] - prefix[y]) * (y - x):
                candidates.popleft()
            else:
                break

        best = max(best, Fraction(prefix[end] - prefix[candidates[0]], end - candidates[0]))

    return [best.numerator, best.denominator]
