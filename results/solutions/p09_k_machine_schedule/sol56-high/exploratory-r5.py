def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    graph = [[] for _ in times]

    def add_edge(source: int, target: int, capacity: int, cost: int) -> None:
        graph[source].append([target, len(graph[target]), capacity, cost])
        graph[target].append([source, len(graph[source]) - 1, 0, -cost])

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source = 0
    sink = len(times) - 1
    flow = 0
    total_cost = 0
    infinity = 10**30

    while flow < k:
        distance = [infinity] * len(times)
        previous_node = [-1] * len(times)
        previous_edge = [-1] * len(times)
        distance[source] = 0

        for _ in range(len(times) - 1):
            changed = False
            for node, edges in enumerate(graph):
                if distance[node] == infinity:
                    continue
                for edge_index, edge in enumerate(edges):
                    target, _, capacity, cost = edge
                    new_distance = distance[node] + cost
                    if capacity > 0 and new_distance < distance[target]:
                        distance[target] = new_distance
                        previous_node[target] = node
                        previous_edge[target] = edge_index
                        changed = True
            if not changed:
                break

        additional_flow = k - flow
        node = sink
        while node != source:
            parent = previous_node[node]
            edge_index = previous_edge[node]
            additional_flow = min(
                additional_flow, graph[parent][edge_index][2]
            )
            node = parent

        node = sink
        while node != source:
            parent = previous_node[node]
            edge_index = previous_edge[node]
            edge = graph[parent][edge_index]
            edge[2] -= additional_flow
            graph[node][edge[1]][2] += additional_flow
            node = parent

        flow += additional_flow
        total_cost += additional_flow * distance[sink]

    return -total_cost
