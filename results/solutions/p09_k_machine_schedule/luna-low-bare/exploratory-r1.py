def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)

    # Residual graph edges: [destination, reverse-edge index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units of flow from the first to last time. Each unit is one printer;
    # negative-cost job edges maximize total pay.
    total_cost = 0
    for _ in range(k):
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        queue = [0]
        dist[0] = 0
        in_queue[0] = True
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False
            for ei, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity and dist[v] > dist[u] + cost:
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
