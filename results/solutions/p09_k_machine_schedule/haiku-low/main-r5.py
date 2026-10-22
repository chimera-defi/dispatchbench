from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    # Min-cost flow on a compressed time line. Each unit of flow is one printer.
    # Idle chain edges carry a printer forward in time at zero cost, and each job
    # is an edge start -> end with capacity 1 and cost -pay.
    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    for s, e, pay in jobs:
        add_edge(idx[s], idx[e], 1, -pay)

    source, sink = 0, n - 1
    INF = float("inf")
    total = 0
    flow = 0

    while flow < k:
        # Bellman-Ford style shortest path (SPFA), since costs may be negative.
        dist = [INF] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        dist[source] = 0
        queue = deque([source])
        in_queue[source] = True

        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for ei, (v, cap, cost, _) in enumerate(graph[u]):
                if cap > 0 and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        # Stop once extra printers can no longer increase the total pay.
        if dist[sink] == INF or dist[sink] >= 0:
            break

        # Find bottleneck along the path, capped by remaining printers.
        push = k - flow
        v = sink
        while v != source:
            u = prev_node[v]
            push = min(push, graph[u][prev_edge[v]][1])
            v = u

        # Augment along the path.
        v = sink
        while v != source:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[1] -= push
            graph[v][edge[3]][1] += push
            v = u

        flow += push
        total += -dist[sink] * push

    return total
