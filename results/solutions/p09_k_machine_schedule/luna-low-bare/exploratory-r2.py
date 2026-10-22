def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Residual graph edges: [to, reverse_edge_index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units of flow; shortest augmenting paths maximize total pay.
    total_cost = 0
    for _ in range(k):
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        dist[0] = 0
        queue = [0]
        in_queue[0] = True
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False
            for ei, edge in enumerate(graph[u]):
                v, _, cap, cost = edge
                if cap and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        v = n - 1
        total_cost += dist[v]
        while v != 0:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

    return -total_cost
