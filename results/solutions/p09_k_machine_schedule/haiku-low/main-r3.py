from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Each edge is [to, capacity, cost, index of reverse edge in graph[to]]
    graph = [[] for _ in range(n)]

    def add_edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    # Time-line edges let up to k machines pass through every gap
    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    # Each job is a unit-capacity edge that earns its pay
    for s, e, p in jobs:
        add_edge(idx[s], idx[e], 1, -p)

    source, sink = 0, n - 1
    INF = float("inf")
    total_cost = 0
    flow = 0

    # Successive shortest paths: push up to k units while a path lowers cost
    while flow < k:
        dist = [INF] * n
        prev = [None] * n
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
                    prev[v] = (u, ei)
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        if dist[sink] >= 0:
            break

        push = k - flow
        v = sink
        while v != source:
            u, ei = prev[v]
            push = min(push, graph[u][ei][1])
            v = u

        v = sink
        while v != source:
            u, ei = prev[v]
            edge = graph[u][ei]
            edge[1] -= push
            graph[v][edge[3]][1] += push
            v = u

        flow += push
        total_cost += push * dist[sink]

    return -total_cost
