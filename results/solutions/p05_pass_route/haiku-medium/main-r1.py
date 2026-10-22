import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    zones = len(prices)
    full = 1 << zones

    # Adjacency with the zone bit for each ride (0 means no zone, never free)
    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = 0 if zone < 0 else (1 << zone)
        adj[u].append((v, cost, bit))
        adj[v].append((u, cost, bit))

    # Zones whose pass can be bought at each stop
    buy = [[] for _ in range(n)]
    for stop, z in stations:
        buy[stop].append(z)

    # State: (stop, mask of bought passes)
    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]  # (cost, stop, mask)

    while pq:
        d, u, mask = heapq.heappop(pq)
        if d > dist[u][mask]:
            continue
        if u == n - 1:
            return d

        # Take a ride; free if its zone pass is already held
        for v, cost, bit in adj[u]:
            nd = d if (mask & bit) else d + cost
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(pq, (nd, v, mask))

        # Buy a pass for a zone available at this stop
        for z in buy[u]:
            zb = 1 << z
            if mask & zb:
                continue
            nm = mask | zb
            nd = d + prices[z]
            if nd < dist[u][nm]:
                dist[u][nm] = nd
                heapq.heappush(pq, (nd, u, nm))

    return -1
