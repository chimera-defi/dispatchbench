def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
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
    total_cost = 0
    flow = 0
    infinity = 10**30

    while flow < k:
        distance = [infinity] * n
        previous = [None] * n
        distance[source] = 0

        for _ in range(n - 1):
            changed = False
            for u in range(n):
                if distance[u] == infinity:
                    continue
                for edge_index, edge in enumerate(graph[u]):
                    v, _, capacity, cost = edge
                    if capacity and distance[u] + cost < distance[v]:
                        distance[v] = distance[u] + cost
                        previous[v] = (u, edge_index)
                        changed = True
            if not changed:
                break

        amount = k - flow
        v = sink
        while v != source:
            u, edge_index = previous[v]
            amount = min(amount, graph[u][edge_index][2])
            v = u

        v = sink
        while v != source:
            u, edge_index = previous[v]
            edge = graph[u][edge_index]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount
        total_cost += amount * distance[sink]

    return -total_cost
