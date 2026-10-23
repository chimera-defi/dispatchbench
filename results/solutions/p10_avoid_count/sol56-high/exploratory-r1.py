def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    if n == 0:
        return 1

    children = [{}]
    terminal = [False]

    for pattern in banned:
        node = 0
        for char in pattern:
            if char not in children[node]:
                children[node][char] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][char]
        terminal[node] = True

    from collections import deque

    failure = [0] * len(children)
    queue = deque(children[0].values())

    while queue:
        node = queue.popleft()
        terminal[node] = terminal[node] or terminal[failure[node]]

        for char, child in children[node].items():
            fallback = failure[node]
            while fallback and char not in children[fallback]:
                fallback = failure[fallback]
            failure[child] = children[fallback].get(char, 0)
            queue.append(child)

    safe_states = [state for state in range(len(children)) if not terminal[state]]
    safe_index = {state: index for index, state in enumerate(safe_states)}
    size = len(safe_states)

    transition = [[0] * size for _ in range(size)]

    for state in safe_states:
        source = safe_index[state]
        for char in alphabet:
            node = state
            while node and char not in children[node]:
                node = failure[node]
            destination = children[node].get(char, 0)

            if not terminal[destination]:
                transition[source][safe_index[destination]] += 1

    def multiply_vector_matrix(vector, matrix):
        result = [0] * size
        for i, value in enumerate(vector):
            if value:
                row = matrix[i]
                for j, coefficient in enumerate(row):
                    if coefficient:
                        result[j] = (result[j] + value * coefficient) % MOD
        return result

    def multiply_matrices(left, right):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            result_row = result[i]
            for k, left_value in enumerate(left[i]):
                if left_value:
                    right_row = right[k]
                    for j, right_value in enumerate(right_row):
                        if right_value:
                            result_row[j] = (
                                result_row[j] + left_value * right_value
                            ) % MOD
        return result

    counts = [0] * size
    counts[safe_index[0]] = 1

    while n:
        if n & 1:
            counts = multiply_vector_matrix(counts, transition)
        n >>= 1
        if n:
            transition = multiply_matrices(transition, transition)

    return sum(counts) % MOD
