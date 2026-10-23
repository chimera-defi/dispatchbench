def weighted_distance_sums(
    n: int, edges: list[list[int]], w: list[int]
) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    order = [0]

    for v in order:
        for u in graph[v]:
            if u != parent[v]:
                parent[u] = v
                order.append(u)

    subtree_weight = w.copy()
    root_sum = 0

    for v in reversed(order):
        if v != 0:
            subtree_weight[parent[v]] += subtree_weight[v]
        root_sum += w[v] * (0 if v == 0 else 1)

    # Accumulate weighted depths without recursion.
    depth = [0] * n
    root_sum = 0
    for v in order[1:]:
        depth[v] = depth[parent[v]] + 1
        root_sum += w[v] * depth[v]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = root_sum

    for v in order[1:]:
        result[v] = (
            result[parent[v]]
            + total_weight
            - 2 * subtree_weight[v]
        )

    return result
