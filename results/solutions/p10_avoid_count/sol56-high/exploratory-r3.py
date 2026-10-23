def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007

    children = [{}]
    terminal = [False]

    for word in banned:
        state = 0
        for char in word:
            if char not in children[state]:
                children[state][char] = len(children)
                children.append({})
                terminal.append(False)
            state = children[state][char]
        terminal[state] = True

    states = len(children)
    failure = [0] * states
    transitions = [[0] * len(alphabet) for _ in range(states)]
    queue = deque()

    for index, char in enumerate(alphabet):
        child = children[0].get(char)
        if child is not None:
            transitions[0][index] = child
            queue.append(child)

    while queue:
        state = queue.popleft()
        terminal[state] |= terminal[failure[state]]

        for index, char in enumerate(alphabet):
            child = children[state].get(char)
            if child is not None:
                failure[child] = transitions[failure[state]][index]
                transitions[state][index] = child
                queue.append(child)
            else:
                transitions[state][index] = transitions[failure[state]][index]

    safe_states = [state for state in range(states) if not terminal[state]]
    safe_index = {state: index for index, state in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for state in safe_states:
        source = safe_index[state]
        for index in range(len(alphabet)):
            target = transitions[state][index]
            if not terminal[target]:
                matrix[source][safe_index[target]] += 1

    vector = [0] * size
    vector[safe_index[0]] = 1

    def multiply_vector(vector, matrix):
        result = [0] * size
        for i, value in enumerate(vector):
            if value:
                row = matrix[i]
                for j, weight in enumerate(row):
                    if weight:
                        result[j] = (result[j] + value * weight) % MOD
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

    while n:
        if n & 1:
            vector = multiply_vector(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % MOD
