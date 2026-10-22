def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    station_zones = [[] for _ in range(n)]
    for stop, zone in stations:
        station_zones[stop].append(zone)

    # Each bit indicates that the corresponding zone pass has been purchased.
    states = 1 << k
    dist = [[float("inf")] * states for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        total, stop, mask = heapq.heappop(heap)
        if total != dist[stop][mask]:
            continue
        if stop == n - 1:
            return total

        for zone in station_zones[stop]:
            bit = 1 << zone
            if not mask & bit:
                new_mask = mask | bit
                new_total = total + prices[zone]
                if new_total < dist[stop][new_mask]:
                    dist[stop][new_mask] = new_total
                    heapq.heappush(heap, (new_total, stop, new_mask))

        for neighbor, cost, zone in graph[stop]:
            ride_cost = cost
            if zone != -1 and mask & (1 << zone):
                ride_cost = 0
            new_total = total + ride_cost
            if new_total < dist[neighbor][mask]:
                dist[neighbor][mask] = new_total
                heapq.heappush(heap, (new_total, neighbor, mask))

    return -1
