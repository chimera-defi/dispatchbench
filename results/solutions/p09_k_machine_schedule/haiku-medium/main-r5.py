def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    # Compress all start/end times into sorted coordinates.
    coords = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(coords)}
    m = len(coords)

    # Edge format: [to, capacity, cost, index of reverse edge in graph[to]]
    graph = [[] for _ in range(m)]

    def add_edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    # Idle time: a machine can move forward in time at no cost.
    for i in range(m - 1):
        add_edge(i, i + 1, k, 0)

    # Each job: one unit of machine flow goes from its start to its end, earning pay.
    for s, e, p in jobs:
        add_edge(idx[s], idx[e], 1, -p)

    source, sink = 0, m - 1
    INF = float("inf")
    flow = 0
    cost = 0

    # Successive shortest paths (Bellman-Ford handles negative costs).
    while flow < k:
        dist = [INF] * m
        prev = [None] * m
        dist[source] = 0

        changed = True
        while changed:
            changed = False
            for u in range(m):
                if dist[u] == INF:
                    continue
                for ei, edge in enumerate(graph[u]):
                    v, cap, c, _ = edge
                    if cap > 0 and dist[u] + c < dist[v]:
                        dist[v] = dist[u] + c
                        prev[v] = (u, ei)
                        changed = True

        if dist[sink] == INF:
            break

        # Find bottleneck along the path.
        d = k - flow
        v = sink
        while v != source:
            u, ei = prev[v]
            d = min(d, graph[u][ei][1])
            v = u

        # Augment the path.
        v = sink
        while v != source:
            u, ei = prev[v]
            edge = graph[u][ei]
            edge[1] -= d
            graph[v][edge[3]][1] += d
            v = u

        flow += d
        cost += d * dist[sink]

    return -cost
