def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zone_count = len(prices)
    # State mask records which zone passes have been bought.
    dist = [[float("inf")] * (1 << zone_count) for _ in range(n)]
    station_zones = [[] for _ in range(n)]
    for stop, zone in stations:
        station_zones[stop].append(zone)

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    dist[0][0] = 0
    queue = [(0, 0, 0)]

    while queue:
        spent, stop, mask = heapq.heappop(queue)
        if spent != dist[stop][mask]:
            continue
        if stop == n - 1:
            return spent

        for zone in station_zones[stop]:
            bit = 1 << zone
            if not mask & bit:
                new_mask = mask | bit
                new_spent = spent + prices[zone]
                if new_spent < dist[stop][new_mask]:
                    dist[stop][new_mask] = new_spent
                    heapq.heappush(queue, (new_spent, stop, new_mask))

        for nxt, cost, zone in graph[stop]:
            ride_cost = cost
            if zone != -1 and mask & (1 << zone):
                ride_cost = 0
            new_spent = spent + ride_cost
            if new_spent < dist[nxt][mask]:
                dist[nxt][mask] = new_spent
                heapq.heappush(queue, (new_spent, nxt, mask))

    return -1
