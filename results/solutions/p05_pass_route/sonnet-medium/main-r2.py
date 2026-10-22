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
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        d, u, m = heapq.heappop(heap)
        if d > dist[u][m]:
            continue
        if u == n - 1:
            return d
        for z in st[u]:
            if not (m >> z) & 1:
                nm = m | (1 << z)
                nd = d + prices[z]
                if nd < dist[u][nm]:
                    dist[u][nm] = nd
                    heapq.heappush(heap, (nd, u, nm))
        for v, c, z in adj[u]:
            if z != -1 and (m >> z) & 1:
                c = 0
            nd = d + c
            if nd < dist[v][m]:
                dist[v][m] = nd
                heapq.heappush(heap, (nd, v, m))
    return -1
