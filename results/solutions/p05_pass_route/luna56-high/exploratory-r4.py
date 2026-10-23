def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    states = 1 << k
    graph = [[] for _ in range(n)]

    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    station_masks = [0] * n
    for stop, zone in stations:
        station_masks[stop] |= 1 << zone

    inf = 10**30
    dist = [[inf] * states for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost, stop, mask = heapq.heappop(heap)
        if cost != dist[stop][mask]:
            continue

        for nxt, ride_cost, zone in graph[stop]:
            extra = 0 if zone >= 0 and (mask & (1 << zone)) else ride_cost
            new_cost = cost + extra
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

        available = station_masks[stop] & ~mask
        while available:
            bit = available & -available
            zone = bit.bit_length() - 1
            new_mask = mask | bit
            new_cost = cost + prices[zone]
            if new_cost < dist[stop][new_mask]:
                dist[stop][new_mask] = new_cost
                heapq.heappush(heap, (new_cost, stop, new_mask))
            available -= bit

    answer = min(dist[n - 1])
    return -1 if answer == inf else answer
