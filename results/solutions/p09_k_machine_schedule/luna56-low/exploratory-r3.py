from collections import deque

def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    source, sink = n, n + 1
    graph = [[] for _ in range(n + 2)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), cap, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    add_edge(source, 0, k, 0)
    add_edge(n - 1, sink, k, 0)

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    flow = 0
    cost = 0

    while flow < k:
        dist = [float("inf")] * (n + 2)
        parent = [None] * (n + 2)
        in_queue = [False] * (n + 2)
        queue = deque([source])
        dist[source] = 0
        in_queue[source] = True

        while queue:
            u = queue.popleft()
            in_queue[u] = False

            for ei, edge in enumerate(graph[u]):
                v, _, cap, edge_cost = edge
                if cap and dist[v] > dist[u] + edge_cost:
                    dist[v] = dist[u] + edge_cost
                    parent[v] = (u, ei)
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        if dist[sink] == float("inf"):
            break

        amount = k - flow
        v = sink
        while v != source:
            u, ei = parent[v]
            amount = min(amount, graph[u][ei][2])
            v = u

        v = sink
        while v != source:
            u, ei = parent[v]
            edge = graph[u][ei]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount
        cost += amount * dist[sink]

    return -cost
