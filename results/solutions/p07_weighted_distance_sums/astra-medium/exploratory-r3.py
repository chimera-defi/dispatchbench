def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    order = [0]
    for u in order:
        for v in adj[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)

    subtree_weight = w.copy()
    result = [0] * n

    for i in range(n - 1, 0, -1):
        u = order[i]
        p = parent[u]
        subtree_weight[p] += subtree_weight[u]
        result[p] += result[u] + subtree_weight[u]

    total_weight = subtree_weight[0]
    for i in range(1, n):
        u = order[i]
        result[u] = result[parent[u]] + total_weight - 2 * subtree_weight[u]

    return result
