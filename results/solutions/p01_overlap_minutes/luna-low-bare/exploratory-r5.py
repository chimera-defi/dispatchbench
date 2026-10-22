def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    events.sort()
    active = 0
    total = 0
    prev_time = None
    i = 0

    while i < len(events):
        time = events[i][0]
        if prev_time is not None and active >= k:
            total += time - prev_time

        delta = 0
        while i < len(events) and events[i][0] == time:
            delta += events[i][1]
            i += 1
        active += delta
        prev_time = time

    return total
