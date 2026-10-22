def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Min-cost flow on a time-line: sending k units from the first to the
    # last time chooses up to k overlapping jobs. Timeline edges have zero
    # cost; each job edge has cost -pay.
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    flow = 0

    while flow < k:
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        queue = [0]
        head = 0
        dist[0] = 0
        in_queue[0] = True

        # SPFA finds a shortest residual path; reverse edges allow replacing
        # previously selected jobs when a better schedule is found.
        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for ei, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        if prev_node[n - 1] == -1:
            break

        v = n - 1
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        flow += 1
        total_cost += dist[n - 1]

    return -total_cost
