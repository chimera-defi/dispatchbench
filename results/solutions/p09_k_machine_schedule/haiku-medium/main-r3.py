from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    # Compress times. Node i is a time point; a unit of flow is one printer.
    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Edge format: [to, capacity, cost, index of reverse edge]
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    # Idle time moves forward with unlimited-by-k capacity (up to k printers).
    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    # Each job is a unit-capacity edge that earns its pay (negative cost).
    for s, e, p in jobs:
        add_edge(idx[s], idx[e], 1, -p)

    src, sink = 0, n - 1
    INF = float("inf")
    total = 0
    flow = 0

    # Successive shortest paths: each augmentation is one more printer.
    # Cost is convex in flow, so stop once the best path no longer helps.
    while flow < k:
        dist = [INF] * n
        in_queue = [False] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[src] = 0
        queue = deque([src])
        in_queue[src] = True

        # SPFA (Bellman-Ford with a queue); residual graph has no negative cycles.
        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for j, (v, cap, cost, _) in enumerate(graph[u]):
                if cap > 0 and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = j
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        if dist[sink] == INF or dist[sink] >= 0:
            break

        # Push as much flow as this path allows (bounded by remaining printers).
        push = k - flow
        v = sink
        while v != src:
            u = prev_node[v]
            push = min(push, graph[u][prev_edge[v]][1])
            v = u

        v = sink
        while v != src:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[1] -= push
            graph[v][edge[3]][1] += push
            v = u

        total += -dist[sink] * push
        flow += push

    return int(total)
