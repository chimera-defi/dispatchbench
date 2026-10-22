def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    from collections import deque

    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)

    # Min-cost flow on a timeline: each of k units of flow represents a printer.
    # Timeline edges have capacity k and zero cost; job edges have capacity 1
    # and cost -pay. Bellman-Ford (SPFA) is used for each augmentation because
    # job costs are negative and the Dijkstra potentials would need a valid
    # initial setup, which the first attempt did not provide.
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    inf = float("inf")

    for _ in range(k):
        dist = [inf] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        dist[0] = 0
        queue = deque([0])
        in_queue[0] = True

        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for ei, (v, capacity, cost, _) in enumerate(graph[u]):
                if capacity > 0 and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        if dist[n - 1] == inf:
            break

        # Push one unit of flow (one printer) along the shortest path.
        v = n - 1
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        total_cost += dist[n - 1]

    return -total_cost
