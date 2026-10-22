def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = {}
    for s, e in meetings:
        if s == e:
            continue
        events[s] = events.get(s, 0) + 1
        events[e] = events.get(e, 0) - 1
    total = 0
    count = 0
    prev = 0
    for t in sorted(events):
        if count >= k:
            total += t - prev
        count += events[t]
        prev = t
    return total
