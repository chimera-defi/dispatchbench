def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    if not jobs:
        return 0

    index = {time: i for i, time in enumerate(times)}
    graph = [[] for _ in times]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)
    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, len(times) - 1
    total_cost = 0

    for _ in range(k):
        dist = [float("inf")] * len(times)
        parent = [None] * len(times)
        dist[source] = 0

        for _ in range(len(times) - 1):
            changed = False
            for u in range(len(times)):
                if dist[u] == float("inf"):
                    continue
                for edge_index, edge in enumerate(graph[u]):
                    v, capacity, cost, _ = edge
                    if capacity and dist[u] + cost < dist[v]:
                        dist[v] = dist[u] + cost
                        parent[v] = (u, edge_index)
                        changed = True
            if not changed:
                break

        v = sink
        while v != source:
            u, edge_index = parent[v]
            edge = graph[u][edge_index]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        total_cost += dist[sink]

    return -total_cost
