def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    station_masks = [0] * n
    for stop, zone in stations:
        station_masks[stop] |= 1 << zone

    num_masks = 1 << len(prices)
    dist = [[float("inf")] * num_masks for _ in range(n)]
    dist[0][0] = 0

    heap = [(0, 0, 0)]

    while heap:
        cost, stop, mask = heapq.heappop(heap)
        if cost != dist[stop][mask]:
            continue
        if stop == n - 1:
            return cost

        available = station_masks[stop] & ~mask
        while available:
            bit = available & -available
            zone = bit.bit_length() - 1
            new_cost = cost + prices[zone]
            new_mask = mask | bit
            if new_cost < dist[stop][new_mask]:
                dist[stop][new_mask] = new_cost
                heapq.heappush(heap, (new_cost, stop, new_mask))
            available -= bit

        for nxt, ride_cost, zone in graph[stop]:
            if zone != -1 and (mask & (1 << zone)):
                ride_cost = 0
            new_cost = cost + ride_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

    return -1
