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
        for neighbor in graph[v]:
            if neighbor == parent[v]:
                continue
            parent[neighbor] = v
            depth[neighbor] = depth[v] + 1
            order.append(neighbor)

    subtree_weight = w.copy()
    total_weight = sum(w)
    result = [0] * n
    result[0] = sum(weight * d for weight, d in zip(w, depth))

    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    for v in order[1:]:
        result[v] = (
            result[parent[v]]
            + total_weight
            - 2 * subtree_weight[v]
        )

    return result
