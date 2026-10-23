def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    station_masks = [0] * n
    for stop, zone in stations:
        station_masks[stop] |= 1 << zone

    masks = 1 << len(prices)
    inf = 10**30
    dist = [[inf] * masks for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost, node, mask = heapq.heappop(heap)
        if cost != dist[node][mask]:
            continue
        if node == n - 1:
            return cost

        available = station_masks[node] & ~mask
        while available:
            bit = available & -available
            available -= bit
            zone = bit.bit_length() - 1
            new_cost = cost + prices[zone]
            new_mask = mask | bit
            if new_cost < dist[node][new_mask]:
                dist[node][new_mask] = new_cost
                heapq.heappush(heap, (new_cost, node, new_mask))

        for nxt, ride_cost, zone in graph[node]:
            if zone >= 0 and (mask & (1 << zone)):
                ride_cost = 0
            new_cost = cost + ride_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

    return -1
