from collections import deque

def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0
    times = sorted({t for s, e, p in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]
    # edge: [to, cap, cost, rev_index]

    def add(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add(i, i + 1, k, 0)
    for s, e, p in jobs:
        add(idx[s], idx[e], 1, -p)

    src, dst = 0, n - 1
    flow = 0
    total = 0
    INF = float('inf')
    while flow < k:
        dist = [INF] * n
        dist[src] = 0
        inq = [False] * n
        prev = [None] * n
        dq = deque([src])
        while dq:
            u = dq.popleft()
            inq[u] = False
            du = dist[u]
            for ei, (v, cap, cost, _) in enumerate(graph[u]):
                if cap > 0 and du + cost < dist[v]:
                    dist[v] = du + cost
                    prev[v] = (u, ei)
                    if not inq[v]:
                        inq[v] = True
                        dq.append(v)
        if dist[dst] == INF or dist[dst] >= 0:
            break
        push = k - flow
        v = dst
        while v != src:
            u, ei = prev[v]
            push = min(push, graph[u][ei][1])
            v = u
        v = dst
        while v != src:
            u, ei = prev[v]
            e = graph[u][ei]
            e[1] -= push
            graph[v][e[3]][1] += push
            v = u
        flow += push
        total += push * dist[dst]
    return -total
