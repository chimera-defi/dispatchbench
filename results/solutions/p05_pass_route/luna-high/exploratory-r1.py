def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    available = [set() for _ in range(n)]
    for stop, zone in stations:
        available[stop].add(zone)

    inf = float("inf")
    dist = [[inf] * n for _ in range(k + 1)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]  # cost, pass layer (0 = none), stop

    while heap:
        cost, layer, stop = heapq.heappop(heap)
        if cost != dist[layer][stop]:
            continue
        if stop == n - 1:
            return cost

        if layer == 0:
            for zone in available[stop]:
                next_layer = zone + 1
                new_cost = cost + prices[zone]
                if new_cost < dist[next_layer][stop]:
                    dist[next_layer][stop] = new_cost
                    heapq.heappush(heap, (new_cost, next_layer, stop))

        for nxt, ride_cost, zone in graph[stop]:
            new_cost = cost + (0 if layer == zone + 1 else ride_cost)
            if new_cost < dist[layer][nxt]:
                dist[layer][nxt] = new_cost
                heapq.heappush(heap, (new_cost, layer, nxt))

    return -1
