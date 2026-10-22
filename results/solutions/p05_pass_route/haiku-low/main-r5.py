import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    k = len(prices)
    full = 1 << k

    # Adjacency list: adj[u] = [(v, cost, zone), ...] for both directions
    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    # Zones purchasable at each stop
    station_zones = [[] for _ in range(n)]
    for stop, z in stations:
        station_zones[stop].append(z)

    # Dijkstra over states (stop, mask of bought passes)
    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]  # (cost, stop, mask)

    while heap:
        d, u, mask = heapq.heappop(heap)
        if d != dist[u][mask]:
            continue
        if u == n - 1:
            return d

        # Buy a pass at this stop
        for z in station_zones[u]:
            bit = 1 << z
            if not mask & bit:
                nmask = mask | bit
                nd = d + prices[z]
                if nd < dist[u][nmask]:
                    dist[u][nmask] = nd
                    heapq.heappush(heap, (nd, u, nmask))

        # Ride to a neighbouring stop
        for v, cost, zone in adj[u]:
            if zone >= 0 and mask & (1 << zone):
                step = 0
            else:
                step = cost
            nd = d + step
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(heap, (nd, v, mask))

    return -1
