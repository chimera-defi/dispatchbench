def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    total_cost = 0
    flow = 0
    inf = 10**30

    while flow < k:
        distance = [inf] * n
        in_queue = [False] * n
        parent = [None] * n
        distance[source] = 0

        queue = [source]
        head = 0
        in_queue[source] = True

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for edge_index, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity and distance[v] > distance[u] + cost:
                    distance[v] = distance[u] + cost
                    parent[v] = (u, edge_index)
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        if distance[sink] == inf:
            break

        amount = k - flow
        v = sink
        while v != source:
            u, edge_index = parent[v]
            amount = min(amount, graph[u][edge_index][1])
            v = u

        v = sink
        while v != source:
            u, edge_index = parent[v]
            edge = graph[u][edge_index]
            reverse_index = edge[3]
            edge[1] -= amount
            graph[v][reverse_index][1] += amount
            v = u

        flow += amount
        total_cost += amount * distance[sink]

    return -total_cost
