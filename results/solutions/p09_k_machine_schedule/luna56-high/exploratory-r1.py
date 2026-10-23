def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    total_cost = 0

    for _ in range(k):
        dist = [float("inf")] * n
        prev = [None] * n
        dist[source] = 0

        for _ in range(n - 1):
            changed = False
            for u in range(n):
                if dist[u] == float("inf"):
                    continue
                for edge_index, edge in enumerate(graph[u]):
                    v, _, capacity, cost = edge
                    if capacity and dist[v] > dist[u] + cost:
                        dist[v] = dist[u] + cost
                        prev[v] = (u, edge_index)
                        changed = True
            if not changed:
                break

        v = sink
        while v != source:
            u, edge_index = prev[v]
            edge = graph[u][edge_index]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

        total_cost += dist[sink]

    return -total_cost
