def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    parent = [-1] * n
    order = [0]
    parent[0] = 0

    for u in order:
        for v in graph[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)

    subtree_weight = w[:]
    for u in reversed(order[1:]):
        subtree_weight[parent[u]] += subtree_weight[u]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = sum(subtree_weight[u] for u in order[1:])

    for u in order[1:]:
        p = parent[u]
        result[u] = result[p] + total_weight - 2 * subtree_weight[u]

    return result
