from collections import deque

def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), cap, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    flow = total_cost = 0
    while flow < k:
        dist = [float("inf")] * n
        parent = [None] * n
        in_queue = [False] * n
        dist[0] = 0
        queue = deque([0])
        in_queue[0] = True

        while queue:
            u = queue.popleft()
            in_queue[u] = False
            for i, edge in enumerate(graph[u]):
                v, _, cap, cost = edge
                if cap and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    parent[v] = (u, i)
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        amount = k - flow
        v = n - 1
        while v != 0:
            u, i = parent[v]
            amount = min(amount, graph[u][i][2])
            v = u

        v = n - 1
        while v != 0:
            u, i = parent[v]
            edge = graph[u][i]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount
        total_cost += amount * dist[n - 1]

    return -total_cost
