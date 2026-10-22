from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    # Time line: each gap carries up to k machines at zero cost (idle time).
    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    # A job is a unit-capacity edge that gains its pay.
    for s, e, pay in jobs:
        add_edge(index[s], index[e], 1, -pay)

    src, snk = 0, n - 1
    INF = float('inf')
    best = 0

    # Successive shortest paths: each unit of flow is one machine.
    for _ in range(k):
        dist = [INF] * n
        prev = [None] * n
        in_queue = [False] * n
        dist[src] = 0
        queue = deque([src])
        in_queue[src] = True

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

        if dist[snk] == INF or dist[snk] >= 0:
            break

        # Push one unit along the shortest path.
        v = snk
        while v != src:
            u, ei = prev[v]
            edge = graph[u][ei]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        best += -dist[snk]

    return best
