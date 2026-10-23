from fractions import Fraction

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)

    for i, value in enumerate(a):
        prefix[i + 1] = prefix[i] + value

    scale = 1 << 35

    def feasible(threshold: int) -> bool:
        minimum = 0

        for end in range(k, n + 1):
            start = end - k
            candidate = prefix[start] * scale - start * threshold
            if candidate < minimum:
                minimum = candidate

            current = prefix[end] * scale - end * threshold
            if current >= minimum:
                return True

        return False

    low = 0
    high = max(a) * scale + 1

    while high - low > 1:
        mid = (low + high) // 2
        if feasible(mid):
            low = mid
        else:
            high = mid

    result = Fraction(low, scale).limit_denominator(n)
    return [result.numerator, result.denominator]
