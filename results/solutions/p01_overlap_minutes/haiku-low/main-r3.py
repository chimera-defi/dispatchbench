def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))
    # Process ends before starts at the same time so touching meetings don't count as overlapping.
    events.sort(key=lambda e: (e[0], e[1]))
    total = 0
    count = 0
    prev = None
    for t, delta in events:
        if prev is not None and count >= k:
            total += t - prev
        count += delta
        prev = t
    return total
