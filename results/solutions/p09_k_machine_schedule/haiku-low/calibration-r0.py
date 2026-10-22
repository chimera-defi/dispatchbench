def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    # Compress all start/end times into graph nodes; time flows left to right.
    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Edge format: [to, capacity, cost, index of reverse edge in graph[to]]
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    # Idle edges let a machine wait between jobs.
    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    # Each job is a unit-capacity edge that earns its pay (negative cost).
    for s, e, p in jobs:
        add_edge(idx[s], idx[e], 1, -p)

    # Min-cost flow of up to k units: each unit is one machine's timeline.
    src, sink = 0, n - 1
    flow = 0
    total_cost = 0
    INF = float("inf")

    while flow < k:
        # Bellman-Ford handles the negative job costs in the residual graph.
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

        # Stop when no path remains or it no longer adds pay.
        if dist[sink] == INF or dist[sink] >= 0:
            break

        # Push as much flow as the bottleneck allows.
        f = k - flow
        v = sink
        while v != src:
            u, ei = prev[v]
            f = min(f, graph[u][ei][1])
            v = u

        v = sink
        while v != src:
            u, ei = prev[v]
            edge = graph[u][ei]
            edge[1] -= f
            graph[v][edge[3]][1] += f
            v = u

        flow += f
        total_cost += f * dist[sink]

    return -total_cost
