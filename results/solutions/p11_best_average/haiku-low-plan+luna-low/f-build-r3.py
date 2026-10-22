from math import gcd


def best_average(a: list[int], k: int) -> list[int]:
    n = len(a)
    prefix = [0] * (n + 1)
    for i, x in enumerate(a):
        prefix[i + 1] = prefix[i] + x

    p, q = prefix[n], n

    while True:
        best_value = 0
        best_sum = best_length = 0
        min_key = 0  # q * prefix[0] - p * 0

        for j in range(k, n + 1):
            i = j - k
            key_i = q * prefix[i] - p * i
            if i == 0 or key_i < min_key:
                min_key = key_i

            key_j = q * prefix[j] - p * j
            value = key_j - min_key
            if value > best_value:
                best_value = value
                best_sum = prefix[j] - prefix[i]  # corrected below using the min-key index
                best_length = j - i

        if best_value == 0:
            break

        # Recover the maximizing start index for this iteration.
        min_key = 0
        min_i = 0
        best_value = 0
        for j in range(k, n + 1):
            i = j - k
            key_i = q * prefix[i] - p * i
            if i == 0 or key_i < min_key:
                min_key = key_i
                min_i = i

            value = q * prefix[j] - p * j - min_key
            if value > best_value:
                best_value = value
                best_sum = prefix[j] - prefix[min_i]
                best_length = j - min_i

        p, q = best_sum, best_length

    divisor = gcd(p, q)
    return [p // divisor, q // divisor]
