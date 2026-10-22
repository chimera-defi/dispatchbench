from collections import deque


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    graph = [[] for _ in times]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        forward = [v, len(graph[v]), capacity, cost]
        reverse = [u, len(graph[u]), 0, -cost]
        graph[u].append(forward)
        graph[v].append(reverse)

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
        queue = deque([source])
        dist[source] = 0
        in_queue[source] = True

        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for edge_index, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity > 0 and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = edge_index
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        if dist[sink] >= 0 or dist[sink] == float("inf"):
            break

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
