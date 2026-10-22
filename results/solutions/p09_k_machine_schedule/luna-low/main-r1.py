def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    jobs.sort(key=lambda job: job[0])
    available = [(0, i) for i in range(k)]
    heapq.heapify(available)
    total = 0

    for start, end, pay in jobs:
        free_at, printer = heapq.heappop(available)
        if free_at <= start:
            total += pay
            heapq.heappush(available, (end, printer))
        else:
            heapq.heappush(available, (free_at, printer))

    return total
