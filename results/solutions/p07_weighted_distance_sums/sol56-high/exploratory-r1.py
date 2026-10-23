def weighted_distance_sums(
    n: int, edges: list[list[int]], w: list[int]
) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    depth = [0] * n
    order = [0]

    for v in order:
        for u in graph[v]:
            if u != parent[v]:
                parent[u] = v
                depth[u] = depth[v] + 1
                order.append(u)

    subtree_weight = w.copy()
    result = [0] * n
    result[0] = sum(weight * depth[v] for v, weight in enumerate(w))

    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    for v in order[1:]:
        result[v] = (
            result[parent[v]]
            + total_weight
            - 2 * subtree_weight[v]
        )

    return result
