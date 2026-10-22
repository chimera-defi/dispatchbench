import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    k = len(prices)
    full = 1 << k

    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    buys = [[] for _ in range(n)]
    for stop, z in stations:
        buys[stop].append(z)

    INF = float('inf')
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]

    while pq:
        d, u, mask = heapq.heappop(pq)
        if d > dist[u][mask]:
            continue

        for z in buys[u]:
            bit = 1 << z
            if not mask & bit:
                nm = mask | bit
                nd = d + prices[z]
                if nd < dist[u][nm]:
                    dist[u][nm] = nd
                    heapq.heappush(pq, (nd, u, nm))

        for v, cost, zone in adj[u]:
            if zone >= 0 and (mask >> zone) & 1:
                nd = d
            else:
                nd = d + cost
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(pq, (nd, v, mask))

    best = min(dist[n - 1])
    return -1 if best == INF else best
