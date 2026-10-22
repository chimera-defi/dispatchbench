import heapq

def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    adj = [[] for _ in range(n)]
    for u, v, c, z in edges:
        adj[u].append((v, c, z))
        adj[v].append((u, c, z))
    st = [[] for _ in range(n)]
    for s, z in stations:
        st[s].append(z)

    k = len(prices)
    M = 1 << k
    INF = float("inf")
    dist = [INF] * (n * M)
    dist[0] = 0
    pq = [(0, 0, 0)]
    while pq:
        d, u, m = heapq.heappop(pq)
        if d > dist[u * M + m]:
            continue
        if u == n - 1:
            return d
        for v, c, z in adj[u]:
            nd = d if (z >= 0 and (m >> z) & 1) else d + c
            idx = v * M + m
            if nd < dist[idx]:
                dist[idx] = nd
                heapq.heappush(pq, (nd, v, m))
        for z in st[u]:
            if not (m >> z) & 1:
                nm = m | (1 << z)
                nd = d + prices[z]
                idx = u * M + nm
                if nd < dist[idx]:
                    dist[idx] = nd
                    heapq.heappush(pq, (nd, u, nm))
    return -1
