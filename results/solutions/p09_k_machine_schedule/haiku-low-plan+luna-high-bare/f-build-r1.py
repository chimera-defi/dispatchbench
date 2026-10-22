from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    graph = [[] for _ in times]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, len(times) - 1
    total_cost = 0

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
                if capacity > 0 and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = edge_i
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        total_cost += dist[sink]
        v = sink
        while v != source:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

    return -total_cost
