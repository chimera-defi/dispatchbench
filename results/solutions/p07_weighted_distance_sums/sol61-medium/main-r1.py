def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    parent = [-1] * n
    parent[0] = 0
    order = [0]

    for u in order:
        for v in adj[u]:
            if v != parent[u]:
                parent[v] = u
                order.append(v)

    subtree_weight = w.copy()
    root_sum = 0

    for u in reversed(order):
        if u != 0:
            root_sum += subtree_weight[u]
            subtree_weight[parent[u]] += subtree_weight[u]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = root_sum

    for u in order:
        if u != 0:
            result[u] = (
                result[parent[u]] + total_weight - 2 * subtree_weight[u]
            )

    return result
