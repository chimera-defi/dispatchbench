from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    graph = [[] for _ in times]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    source, sink = 0, len(times) - 1

    for _ in range(k):
        dist = [float("inf")] * len(times)
        prev_node = [-1] * len(times)
        prev_edge = [-1] * len(times)
        in_queue = [False] * len(times)
        dist[source] = 0
        queue = deque([source])
        in_queue[source] = True

        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for edge_i, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = edge_i
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        amount = k
        v = sink
        while v != source:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            amount = min(amount, edge[2])
            v = u

        v = sink
        while v != source:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        total_cost += amount * dist[sink]

    return -total_cost
