def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    for _ in range(k):
        dist = [float("inf")] * n
        parent = [None] * n
        dist[0] = 0

        for _ in range(n - 1):
            changed = False
            for u in range(n):
                if dist[u] == float("inf"):
                    continue
                for edge_i, edge in enumerate(graph[u]):
                    v, capacity, cost, _ = edge
                    if capacity and dist[u] + cost < dist[v]:
                        dist[v] = dist[u] + cost
                        parent[v] = (u, edge_i)
                        changed = True
            if not changed:
                break

        v = n - 1
        while v != 0:
            u, edge_i = parent[v]
            edge = graph[u][edge_i]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        total_cost += dist[n - 1]

    return -total_cost
