def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    # Compress all start/end times into graph nodes.
    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Min-cost flow graph. Edges are stored in pairs (forward at e, reverse at e ^ 1).
    to: list[int] = []
    cap: list[int] = []
    cost: list[int] = []
    graph: list[list[int]] = [[] for _ in range(n)]

    def add_edge(u: int, v: int, c: int, w: int) -> None:
        graph[u].append(len(to))
        to.append(v)
        cap.append(c)
        cost.append(w)
        graph[v].append(len(to))
        to.append(u)
        cap.append(0)
        cost.append(-w)

    # Idle chain: up to k units of flow can always pass through with zero cost.
    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    # Each job is a unit-capacity edge that earns its pay (negative cost).
    for s, e, pay in jobs:
        add_edge(idx[s], idx[e], 1, -pay)

    source, sink = 0, n - 1
    INF = float("inf")
    total_flow = 0
    total_cost = 0

    while total_flow < k:
        # Bellman-Ford handles the negative job costs in the residual graph.
        dist = [INF] * n
        prev_edge = [-1] * n
        dist[source] = 0
        for _ in range(n - 1):
            updated = False
            for e in range(len(to)):
                if cap[e] <= 0:
                    continue
                u = to[e ^ 1]
                v = to[e]
                if dist[u] != INF and dist[u] + cost[e] < dist[v]:
                    dist[v] = dist[u] + cost[e]
                    prev_edge[v] = e
                    updated = True
            if not updated:
                break

        # No further profit possible from another machine.
        if dist[sink] == INF or dist[sink] >= 0:
            break

        # Push as much as the bottleneck allows along the shortest path.
        push = k - total_flow
        v = sink
        while v != source:
            e = prev_edge[v]
            push = min(push, cap[e])
            v = to[e ^ 1]

        v = sink
        while v != source:
            e = prev_edge[v]
            cap[e] -= push
            cap[e ^ 1] += push
            v = to[e ^ 1]

        total_flow += push
        total_cost += push * dist[sink]

    return -total_cost
