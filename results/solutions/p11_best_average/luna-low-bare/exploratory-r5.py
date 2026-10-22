from fractions import Fraction
from collections import deque

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, value in enumerate(a, 1):
        prefix[i] = prefix[i - 1] + value

    candidates = deque()
    best_num, best_den = 0, 1

    for end in range(k, n + 1):
        start = end - k
        while len(candidates) >= 2:
            x, y = candidates[0], candidates[1]
            if (prefix[y] - prefix[x]) * (end - y) >= (prefix[end] - prefix[y]) * (y - x):
                candidates.popleft()
            else:
                break

        start_best = candidates[0]
        num = prefix[end] - prefix[start_best]
        den = end - start_best
        if num * best_den > best_num * den:
            best_num, best_den = num, den

        while len(candidates) >= 2:
            x, y = candidates[-2], candidates[-1]
            if (prefix[y] - prefix[x]) * (end - y) >= (prefix[end] - prefix[y]) * (y - x):
                candidates.pop()
            else:
                break
        candidates.append(end)

    divisor = __import__("math").gcd(best_num, best_den)
    return [best_num // divisor, best_den // divisor]
