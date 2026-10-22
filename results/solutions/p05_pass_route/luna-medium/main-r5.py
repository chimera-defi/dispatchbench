def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    from heapq import heappush, heappop

    k = len(prices)
    full_mask = (1 << k) - 1

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    available = [[] for _ in range(n)]
    for stop, zone in stations:
        available[stop].append(zone)

    inf = float("inf")
    dist = [[inf] * (1 << k) for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost, stop, mask = heappop(heap)
        if cost != dist[stop][mask]:
            continue
        if stop == n - 1:
            return cost

        for zone in available[stop]:
            bit = 1 << zone
            if not mask & bit:
                new_mask = mask | bit
                new_cost = cost + prices[zone]
                if new_cost < dist[stop][new_mask]:
                    dist[stop][new_mask] = new_cost
                    heappush(heap, (new_cost, stop, new_mask))

        for nxt, ride_cost, zone in graph[stop]:
            new_cost = cost
            if zone == -1 or not (mask & (1 << zone)):
                new_cost += ride_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heappush(heap, (new_cost, nxt, mask))

    return -1
