def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    source, sink = 0, n - 1

    for _ in range(k):
        dist = [float("inf")] * n
        parent = [None] * n
        dist[source] = 0

        for _ in range(n - 1):
            changed = False
            for u in range(n):
                if dist[u] == float("inf"):
                    continue
                for edge_index, edge in enumerate(graph[u]):
                    v, _, capacity, cost = edge
                    if capacity > 0 and dist[u] + cost < dist[v]:
                        dist[v] = dist[u] + cost
                        parent[v] = (u, edge_index)
                        changed = True
            if not changed:
                break

        flow = k
        v = sink
        while v != source:
            u, edge_index = parent[v]
            flow = min(flow, graph[u][edge_index][2])
            v = u

        v = sink
        while v != source:
            u, edge_index = parent[v]
            edge = graph[u][edge_index]
            edge[2] -= flow
            graph[v][edge[1]][2] += flow
            v = u

        total_cost += flow * dist[sink]

    return -total_cost
