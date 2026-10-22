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
            if parent[v] == -1:
                parent[v] = u
                order.append(v)

    subtree_weight = w[:]
    for u in reversed(order[1:]):
        subtree_weight[parent[u]] += subtree_weight[u]

    total_weight = subtree_weight[0]
    result = [0] * n

    # Sum distances from the root, computed using each node's depth.
    depth = [0] * n
    for u in order[1:]:
        depth[u] = depth[parent[u]] + 1
    result[0] = sum(w[u] * depth[u] for u in range(n))

    for u in order[1:]:
        p = parent[u]
        result[u] = result[p] + total_weight - 2 * subtree_weight[u]

    return result
