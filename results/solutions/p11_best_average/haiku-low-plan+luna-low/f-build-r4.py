from math import gcd

def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    p, q = sum(a), n

    while True:
        prefix = [0] * (n + 1)
        for i, value in enumerate(a):
            prefix[i + 1] = prefix[i] + q * value - p

        min_prefix = prefix[0]
        min_index = 0
        best_sum = None
        best_start = best_end = 0

        for end in range(k, n + 1):
            start_candidate = end - k
            if prefix[start_candidate] < min_prefix:
                min_prefix = prefix[start_candidate]
                min_index = start_candidate

            current_sum = prefix[end] - min_prefix
            if best_sum is None or current_sum > best_sum:
                best_sum = current_sum
                best_start = min_index
                best_end = end

        if best_sum <= 0:
            divisor = gcd(p, q)
            return [p // divisor, q // divisor]

        p = sum(a[best_start:best_end])
        q = best_end - best_start
