def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    available = [[] for _ in range(n)]
    for stop, zone in stations:
        available[stop].append(zone)

    # State mask records which zone passes have been purchased.
    states = 1 << k
    inf = float("inf")
    dist = [[inf] * states for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost_so_far, stop, mask = heapq.heappop(heap)
        if cost_so_far != dist[stop][mask]:
            continue
        if stop == n - 1:
            return cost_so_far

        for zone in available[stop]:
            bit = 1 << zone
            if not mask & bit:
                new_cost = cost_so_far + prices[zone]
                if new_cost < dist[stop][mask | bit]:
                    dist[stop][mask | bit] = new_cost
                    heapq.heappush(heap, (new_cost, stop, mask | bit))

        for nxt, ride_cost, zone in graph[stop]:
            edge_cost = ride_cost
            if zone != -1 and mask & (1 << zone):
                edge_cost = 0
            new_cost = cost_so_far + edge_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

    return -1
