def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for s, e in meetings:
        if s < e:
            events.append((s, 1))
            events.append((e, -1))
    events.sort()
    total = 0
    count = 0
    prev = 0
    for t, d in events:
        if count >= k:
            total += t - prev
        count += d
        prev = t
    return total
