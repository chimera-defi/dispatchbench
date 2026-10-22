def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    parent[0] = 0
    order = [0]

    for v in order:
        for u in adj[v]:
            if u != parent[v]:
                parent[u] = v
                order.append(u)

    subtree_weight = w.copy()
    root_sum = 0

    for i in range(n - 1, 0, -1):
        v = order[i]
        root_sum += subtree_weight[v]
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = root_sum

    for i in range(1, n):
        v = order[i]
        result[v] = result[parent[v]] + total_weight - 2 * subtree_weight[v]

    return result
