def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    depth = [0] * n
    order = [0]
    parent[0] = 0

    for v in order:
        for neighbor in graph[v]:
            if parent[neighbor] == -1:
                parent[neighbor] = v
                depth[neighbor] = depth[v] + 1
                order.append(neighbor)

    subtree_weight = w[:]
    total_weight = sum(w)
    root_sum = sum(w[v] * depth[v] for v in range(n))
    result = [0] * n
    result[0] = root_sum

    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree_weight[v]

    return result
