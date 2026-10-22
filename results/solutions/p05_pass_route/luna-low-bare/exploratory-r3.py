def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zone_count = len(prices)
    # State: stop and bitmask of passes already purchased.
    state_count = 1 << zone_count
    dist = [[float("inf")] * state_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    passes_at = [[] for _ in range(n)]
    for stop, zone in stations:
        passes_at[stop].append(zone)

    while heap:
        total, stop, mask = heapq.heappop(heap)
        if total != dist[stop][mask]:
            continue
        if stop == n - 1:
            return total

        for zone in passes_at[stop]:
            bit = 1 << zone
            if not mask & bit:
                new_mask = mask | bit
                new_total = total + prices[zone]
                if new_total < dist[stop][new_mask]:
                    dist[stop][new_mask] = new_total
                    heapq.heappush(heap, (new_total, stop, new_mask))

        for nxt, cost, zone in graph[stop]:
            ride_cost = cost
            if zone != -1 and mask & (1 << zone):
                ride_cost = 0
            new_total = total + ride_cost
            if new_total < dist[nxt][mask]:
                dist[nxt][mask] = new_total
                heapq.heappush(heap, (new_total, nxt, mask))

    return -1
