def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Min-cost flow on the time-line DAG. Sending k units from the first
    # to the last time selects up to k overlapping jobs.
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    source, sink = 0, n - 1

    # Successive shortest augmenting paths; potentials keep reduced costs
    # nonnegative after the initial acyclic graph.
    potential = [0] * n
    for _ in range(k):
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[source] = 0
        used = [False] * n

        for _ in range(n):
            u = -1
            for v in range(n):
                if not used[v] and dist[v] < float("inf") and (
                    u == -1 or dist[v] < dist[u]
                ):
                    u = v
            if u == -1:
                break
            used[u] = True

            for ei, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity <= 0:
                    continue
                reduced = cost + potential[u] - potential[v]
                nd = dist[u] + reduced
                if nd < dist[v]:
                    dist[v] = nd
                    prev_node[v] = u
                    prev_edge[v] = ei

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        if prev_node[sink] == -1:
            break

        v = sink
        while v != source:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            total_cost += edge[2]
            v = u

    return -total_cost
