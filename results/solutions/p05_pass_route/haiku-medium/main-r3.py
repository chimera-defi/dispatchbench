import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    k = len(prices)
    full = 1 << k

    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    station_zones = [[] for _ in range(n)]
    for stop, z in stations:
        station_zones[stop].append(z)

    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        d, u, mask = heapq.heappop(heap)
        if d > dist[u][mask]:
            continue
        if u == n - 1:
            return d

        for v, cost, zone in adj[u]:
            if zone == -1 or (mask >> zone) & 1:
                w = 0
            else:
                w = cost
            nd = d + w
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(heap, (nd, v, mask))

        for z in station_zones[u]:
            bit = 1 << z
            if mask & bit:
                continue
            nm = mask | bit
            nd = d + prices[z]
            if nd < dist[u][nm]:
                dist[u][nm] = nd
                heapq.heappush(heap, (nd, u, nm))

    return -1
