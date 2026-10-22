from collections import defaultdict


def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    deltas = defaultdict(int)
    for start, end in meetings:
        if start == end:
            continue
        deltas[start] += 1
        deltas[end] -= 1

    total = 0
    active = 0
    prev = 0
    for t in sorted(deltas):
        if active >= k:
            total += t - prev
        active += deltas[t]
        prev = t
    return total
