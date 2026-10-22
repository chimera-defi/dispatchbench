def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zone_count = len(prices)
    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    station_zones = [[] for _ in range(n)]
    for stop, zone in stations:
        station_zones[stop].append(zone)

    masks = 1 << zone_count
    dist = [[float("inf")] * masks for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost_so_far, stop, mask = heapq.heappop(heap)
        if cost_so_far != dist[stop][mask]:
            continue
        if stop == n - 1:
            return cost_so_far

        for zone in station_zones[stop]:
            bit = 1 << zone
            if not mask & bit:
                new_cost = cost_so_far + prices[zone]
                new_mask = mask | bit
                if new_cost < dist[stop][new_mask]:
                    dist[stop][new_mask] = new_cost
                    heapq.heappush(heap, (new_cost, stop, new_mask))

        for nxt, ride_cost, zone in graph[stop]:
            new_cost = cost_so_far
            if zone == -1 or not (mask & (1 << zone)):
                new_cost += ride_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

    return -1
