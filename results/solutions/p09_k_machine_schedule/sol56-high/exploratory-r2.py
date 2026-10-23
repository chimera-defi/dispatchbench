def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    from collections import deque

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(source: int, target: int, capacity: int, cost: int) -> None:
        graph[source].append([target, capacity, cost, len(graph[target])])
        graph[target].append([source, 0, -cost, len(graph[source]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    flow = 0
    total_cost = 0

    while flow < k:
        distance = [float("inf")] * n
        previous_node = [-1] * n
        previous_edge = [-1] * n
        in_queue = [False] * n

        distance[source] = 0
        queue = deque([source])
        in_queue[source] = True

        while queue:
            node = queue.popleft()
            in_queue[node] = False

            for edge_index, edge in enumerate(graph[node]):
                target, capacity, cost, _ = edge
                new_distance = distance[node] + cost
                if capacity > 0 and new_distance < distance[target]:
                    distance[target] = new_distance
                    previous_node[target] = node
                    previous_edge[target] = edge_index

                    if not in_queue[target]:
                        queue.append(target)
                        in_queue[target] = True

        added_flow = k - flow
        node = sink
        while node != source:
            parent = previous_node[node]
            edge_index = previous_edge[node]
            added_flow = min(added_flow, graph[parent][edge_index][1])
            node = parent

        node = sink
        while node != source:
            parent = previous_node[node]
            edge_index = previous_edge[node]
            edge = graph[parent][edge_index]
            reverse_index = edge[3]

            edge[1] -= added_flow
            graph[node][reverse_index][1] += added_flow
            node = parent

        flow += added_flow
        total_cost += added_flow * distance[sink]

    return -total_cost
