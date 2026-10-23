def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    order = [0]
    parent[0] = n

    for v in order:
        for u in graph[v]:
            if u != parent[v]:
                parent[u] = v
                order.append(u)

    subtree_weight = w[:]
    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = sum(w[u] * depth for u, depth in zip(order, range(n)))

    for v in order[1:]:
        result[v] = result[parent[v]] + total_weight - 2 * subtree_weight[v]

    return result
