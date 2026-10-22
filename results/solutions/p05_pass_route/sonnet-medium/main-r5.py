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
    full = 1 << k
    INF = float("inf")
    dist = [INF] * (n * full)
    dist[0] = 0
    pq = [(0, 0, 0)]
    while pq:
        d, u, m = heapq.heappop(pq)
        if d > dist[u * full + m]:
            continue
        if u == n - 1:
            return d
        for z in st[u]:
            if not (m >> z) & 1:
                nm = m | (1 << z)
                nd = d + prices[z]
                if nd < dist[u * full + nm]:
                    dist[u * full + nm] = nd
                    heapq.heappush(pq, (nd, u, nm))
        for v, c, z in adj[u]:
            if z >= 0 and (m >> z) & 1:
                nd = d
            else:
                nd = d + c
            if nd < dist[v * full + m]:
                dist[v * full + m] = nd
                heapq.heappush(pq, (nd, v, m))
    return -1
