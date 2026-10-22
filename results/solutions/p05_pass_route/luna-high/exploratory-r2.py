def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zone_count = len(prices)
    state_count = 1 << zone_count
    graph = [[] for _ in range(n)]

    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    inf = float("inf")
    dist = [[inf] * n for _ in range(state_count)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        cost_so_far, mask, stop = heapq.heappop(heap)
        if cost_so_far != dist[mask][stop]:
            continue
        if stop == n - 1:
            return cost_so_far

        options = available[stop] & ~mask
        while options:
            bit = options & -options
            options -= bit
            zone = bit.bit_length() - 1
            new_mask = mask | bit
            new_cost = cost_so_far + prices[zone]
            if new_cost < dist[new_mask][stop]:
                dist[new_mask][stop] = new_cost
                heapq.heappush(heap, (new_cost, new_mask, stop))

        for neighbor, ride_cost, zone in graph[stop]:
            actual_cost = ride_cost
            if zone >= 0 and (mask & (1 << zone)):
                actual_cost = 0
            new_cost = cost_so_far + actual_cost
            if new_cost < dist[mask][neighbor]:
                dist[mask][neighbor] = new_cost
                heapq.heappush(heap, (new_cost, mask, neighbor))

    return -1
