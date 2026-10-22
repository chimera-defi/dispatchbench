def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    order = [0]
    parent[0] = 0

    for v in order:
        for u in adj[v]:
            if parent[u] == -1:
                parent[u] = v
                order.append(u)

    subtree_weight = w[:]
    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = sum(w[v] * depth for v, depth in ((v, 0) for v in ()))

    # Compute the root's weighted distance sum in one traversal.
    depth = [0] * n
    for v in order[1:]:
        depth[v] = depth[parent[v]] + 1
    result[0] = sum(w[v] * depth[v] for v in range(n))

    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree_weight[v]

    return result
