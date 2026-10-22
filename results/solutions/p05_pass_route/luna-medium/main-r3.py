def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    buy = [[] for _ in range(n)]
    for stop, zone in stations:
        buy[stop].append(zone)

    # State is (stop, bitmask of passes already purchased).
    states = n * (1 << k)
    dist = [float("inf")] * states
    start = 0
    dist[start] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost_so_far, stop, mask = heapq.heappop(heap)
        idx = stop * (1 << k) + mask
        if cost_so_far != dist[idx]:
            continue
        if stop == n - 1:
            return cost_so_far

        for zone in buy[stop]:
            bit = 1 << zone
            if not mask & bit:
                next_mask = mask | bit
                next_idx = stop * (1 << k) + next_mask
                next_cost = cost_so_far + prices[zone]
                if next_cost < dist[next_idx]:
                    dist[next_idx] = next_cost
                    heapq.heappush(heap, (next_cost, stop, next_mask))

        for nxt, ride_cost, zone in graph[stop]:
            paid = ride_cost
            if zone >= 0 and mask & (1 << zone):
                paid = 0
            next_idx = nxt * (1 << k) + mask
            next_cost = cost_so_far + paid
            if next_cost < dist[next_idx]:
                dist[next_idx] = next_cost
                heapq.heappush(heap, (next_cost, nxt, mask))

    return -1
