def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    parent = [-1] * n
    order = [0]
    parent[0] = 0

    for v in order:
        for u in graph[v]:
            if parent[u] == -1:
                parent[u] = v
                order.append(u)

    subtree_weight = w[:]
    subtree_distance = [0] * n

    for v in reversed(order[1:]):
        p = parent[v]
        subtree_weight[p] += subtree_weight[v]
        subtree_distance[p] += subtree_distance[v] + subtree_weight[v]

    result = [0] * n
    result[0] = subtree_distance[0]

    total_weight = subtree_weight[0]
    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree_weight[v]

    return result
