def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(source: int, target: int, capacity: int, cost: int) -> None:
        graph[source].append([target, len(graph[target]), capacity, cost])
        graph[target].append([source, len(graph[source]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    remaining_flow = k
    total_cost = 0
    infinity = 10**30

    while remaining_flow:
        distance = [infinity] * n
        previous_vertex = [-1] * n
        previous_edge = [-1] * n
        distance[source] = 0

        for _ in range(n - 1):
            changed = False
            for vertex in range(n):
                if distance[vertex] == infinity:
                    continue
                for edge_index, edge in enumerate(graph[vertex]):
                    target, _, capacity, cost = edge
                    candidate = distance[vertex] + cost
                    if capacity > 0 and candidate < distance[target]:
                        distance[target] = candidate
                        previous_vertex[target] = vertex
                        previous_edge[target] = edge_index
                        changed = True
            if not changed:
                break

        flow = remaining_flow
        vertex = sink
        while vertex != source:
            parent = previous_vertex[vertex]
            edge_index = previous_edge[vertex]
            flow = min(flow, graph[parent][edge_index][2])
            vertex = parent

        vertex = sink
        while vertex != source:
            parent = previous_vertex[vertex]
            edge_index = previous_edge[vertex]
            edge = graph[parent][edge_index]
            edge[2] -= flow
            graph[vertex][edge[1]][2] += flow
            vertex = parent

        remaining_flow -= flow
        total_cost += flow * distance[sink]

    return -total_cost
