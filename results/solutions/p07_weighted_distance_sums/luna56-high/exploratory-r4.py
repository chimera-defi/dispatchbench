def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    parent = [-1] * n
    depth = [0] * n
    order = [0]
    parent[0] = n

    for u in order:
        for v in graph[u]:
            if v != parent[u]:
                parent[v] = u
                depth[v] = depth[u] + 1
                order.append(v)

    total_weight = sum(w)
    root_sum = sum(w[u] * depth[u] for u in range(n))

    subtree_weight = w[:]
    for u in reversed(order[1:]):
        subtree_weight[parent[u]] += subtree_weight[u]

    result = [0] * n
    result[0] = root_sum

    for u in order[1:]:
        p = parent[u]
        result[u] = result[p] + total_weight - 2 * subtree_weight[u]

    return result
