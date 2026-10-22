def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Edge: [to, capacity, cost, index of reverse edge in graph[to]]
    graph = [[] for _ in range(n)]

    def add_edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    # Unused machines move forward in time at zero cost
    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    # Each job is an edge that earns its pay when used
    for s, e, p in jobs:
        add_edge(idx[s], idx[e], 1, -p)

    src, snk = 0, n - 1
    flow = 0
    total_cost = 0

    # Successive shortest paths (Bellman-Ford handles negative costs)
    while flow < k:
        INF = float("inf")
        dist = [INF] * n
        dist[src] = 0
        prev = [None] * n

        for _ in range(n):
            updated = False
            for u in range(n):
                if dist[u] == INF:
                    continue
                for ei, (v, cap, cost, _) in enumerate(graph[u]):
                    if cap > 0 and dist[u] + cost < dist[v]:
                        dist[v] = dist[u] + cost
                        prev[v] = (u, ei)
                        updated = True
            if not updated:
                break

        if dist[snk] == INF:
            break

        # Find bottleneck along the augmenting path
        f = k - flow
        v = snk
        while v != src:
            u, ei = prev[v]
            f = min(f, graph[u][ei][1])
            v = u

        # Push flow along the path
        v = snk
        while v != src:
            u, ei = prev[v]
            edge = graph[u][ei]
            edge[1] -= f
            graph[v][edge[3]][1] += f
            v = u

        flow += f
        total_cost += f * dist[snk]

    return -total_cost
