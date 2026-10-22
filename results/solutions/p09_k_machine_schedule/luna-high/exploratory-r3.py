def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

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

    source, sink = 0, n - 1
    flow = total_cost = 0

    while flow < k:
        dist = [float("inf")] * n
        parent_node = [-1] * n
        parent_edge = [-1] * n
        dist[source] = 0

        for _ in range(n - 1):
            changed = False
            for u in range(n):
                if dist[u] == float("inf"):
                    continue
                for ei, edge in enumerate(graph[u]):
                    v, _, capacity, cost = edge
                    if capacity and dist[v] > dist[u] + cost:
                        dist[v] = dist[u] + cost
                        parent_node[v] = u
                        parent_edge[v] = ei
                        changed = True
            if not changed:
                break

        amount = k - flow
        v = sink
        while v != source:
            u = parent_node[v]
            ei = parent_edge[v]
            amount = min(amount, graph[u][ei][2])
            v = u

        v = sink
        while v != source:
            u = parent_node[v]
            ei = parent_edge[v]
            edge = graph[u][ei]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount
        total_cost += amount * dist[sink]

    return -total_cost
