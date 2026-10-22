def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * n
    depth = [0] * n
    order = [0]
    parent[0] = 0

    for v in order:
        for nei in adj[v]:
            if parent[nei] == -1:
                parent[nei] = v
                depth[nei] = depth[v] + 1
                order.append(nei)

    subtree_weight = w[:]
    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    result = [0] * n
    result[0] = sum(w[v] * depth[v] for v in range(n))

    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree_weight[v]

    return result
