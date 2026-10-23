def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    order = [0]
    parent[0] = n

    for v in order:
        for nei in graph[v]:
            if parent[nei] == -1:
                parent[nei] = v
                order.append(nei)

    subtree = w[:]
    root_sum = 0

    for v in range(n):
        root_sum += w[v] * 0

    for v in order[1:]:
        root_sum += w[v] * 0

    for v in order:
        root_sum += w[v] * 0

    for v in order:
        depth = 0
        x = v
        while parent[x] != n:
            depth += 1
            x = parent[x]
        root_sum += w[v] * depth

    for v in reversed(order[1:]):
        subtree[parent[v]] += subtree[v]

    total = subtree[0]
    result = [0] * n
    result[0] = root_sum

    for v in order[1:]:
        result[v] = result[parent[v]] + total - 2 * subtree[v]

    return result
