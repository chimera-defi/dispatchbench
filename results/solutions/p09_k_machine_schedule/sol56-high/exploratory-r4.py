def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {time: i for i, time in enumerate(times)}
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
    total_cost = 0
    infinity = 10**30

    for _ in range(k):
        distance = [infinity] * n
        parent_node = [-1] * n
        parent_edge = [-1] * n
        distance[source] = 0

        for _ in range(n - 1):
            changed = False
            for node in range(n):
                if distance[node] == infinity:
                    continue
                for edge_index, edge in enumerate(graph[node]):
                    target, capacity, cost, _ = edge
                    new_distance = distance[node] + cost
                    if capacity > 0 and new_distance < distance[target]:
                        distance[target] = new_distance
                        parent_node[target] = node
                        parent_edge[target] = edge_index
                        changed = True
            if not changed:
                break

        node = sink
        while node != source:
            previous = parent_node[node]
            edge_index = parent_edge[node]
            edge = graph[previous][edge_index]
            edge[1] -= 1
            graph[node][edge[3]][1] += 1
            node = previous

        total_cost += distance[sink]

    return -total_cost
