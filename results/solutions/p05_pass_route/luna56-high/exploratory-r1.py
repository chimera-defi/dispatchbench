def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zone_count = len(prices)
    state_count = 1 << zone_count

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    buy_masks = [0] * n
    for stop, zone in stations:
        buy_masks[stop] |= 1 << zone

    inf = 10**30
    dist = [[inf] * state_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        current, stop, mask = heapq.heappop(heap)
        if current != dist[stop][mask]:
            continue
        if stop == n - 1:
            return current

        available = buy_masks[stop] & ~mask
        while available:
            bit = available & -available
            zone = bit.bit_length() - 1
            new_cost = current + prices[zone]
            new_mask = mask | bit
            if new_cost < dist[stop][new_mask]:
                dist[stop][new_mask] = new_cost
                heapq.heappush(heap, (new_cost, stop, new_mask))
            available -= bit

        for nxt, cost, zone in graph[stop]:
            ride_cost = 0 if zone >= 0 and (mask & (1 << zone)) else cost
            new_cost = current + ride_cost
            if new_cost < dist[nxt][mask]:
                dist[nxt][mask] = new_cost
                heapq.heappush(heap, (new_cost, nxt, mask))

    return -1
