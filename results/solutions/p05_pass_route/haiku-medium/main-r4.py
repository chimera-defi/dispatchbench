import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    z_count = len(prices)
    full = 1 << z_count

    # buyable[stop] = bitmask of zones whose pass can be bought at that stop
    buyable = [0] * n
    for stop, z in stations:
        buyable[stop] |= 1 << z

    # adjacency list, undirected
    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]  # (cost, node, mask)

    while pq:
        d, u, mask = heapq.heappop(pq)
        if d > dist[u][mask]:
            continue
        if u == n - 1:
            return d

        # buy any available pass at this stop
        avail = buyable[u] & ~mask
        for z in range(z_count):
            if avail >> z & 1:
                nmask = mask | (1 << z)
                nd = d + prices[z]
                if nd < dist[u][nmask]:
                    dist[u][nmask] = nd
                    heapq.heappush(pq, (nd, u, nmask))

        # take rides
        for v, cost, zone in adj[u]:
            if zone != -1 and mask >> zone & 1:
                w = 0
            else:
                w = cost
            nd = d + w
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(pq, (nd, v, mask))

    best = min(dist[n - 1]) if n - 1 >= 0 else INF
    return -1 if best == INF else best
