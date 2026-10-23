def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zones = len(prices)
    masks = 1 << zones
    graph = [[] for _ in range(n)]

    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    inf = 10**30
    dist = [[inf] * masks for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost, stop, mask = heapq.heappop(heap)
        if cost != dist[stop][mask]:
            continue
        if stop == n - 1:
            return cost

        can_buy = available[stop] & ~mask
        while can_buy:
            bit = can_buy & -can_buy
            can_buy -= bit
            zone = bit.bit_length() - 1
            new_mask = mask | bit
            new_cost = cost + prices[zone]
            if new_cost < dist[stop][new_mask]:
                dist[stop][new_mask] = new_cost
                heapq.heappush(heap, (new_cost, stop, new_mask))

        for nxt, ride_cost, zone in graph[stop]:
            actual_cost = 0 if zone >= 0 and (mask & (1 << zone)) else ride_cost
            new_cost = cost + actual_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

    return -1
