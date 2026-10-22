def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Residual edge: [destination, reverse-edge index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units of flow from the first to the last time. Each unit
    # represents one printer's schedule; interval edges earn their pay.
    total_cost = 0
    source, sink = 0, n - 1

    for _ in range(k):
        dist = [float("inf")] * n
        parent_node = [-1] * n
        parent_edge = [-1] * n
        in_queue = [False] * n
        dist[source] = 0
        queue = [source]
        in_queue[source] = True
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for ei, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    parent_node[v] = u
                    parent_edge[v] = ei
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        if dist[sink] == float("inf"):
            break

        total_cost += dist[sink]
        v = sink
        while v != source:
            u = parent_node[v]
            ei = parent_edge[v]
            edge = graph[u][ei]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

    return -total_cost
