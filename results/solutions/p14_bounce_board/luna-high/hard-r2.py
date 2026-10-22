from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    transitions = {}
    reachable = {0}
    queue = [0]

    while queue:
        pos = queue.pop()
        counts = {}
        for roll in range(1, m + 1):
            landing = pos + roll
            if landing > n:
                landing = 2 * n - landing
            dest = resolve(landing)
            counts[dest] = counts.get(dest, 0) + 1
            if dest != n and dest not in reachable:
                reachable.add(dest)
                queue.append(dest)
        transitions[pos] = counts

    reverse = {pos: [] for pos in reachable}
    can_finish = set()

    for pos, counts in transitions.items():
        for dest in counts:
            if dest == n:
                can_finish.add(pos)
            else:
                reverse[dest].append(pos)

    queue = list(can_finish)
    while queue:
        pos = queue.pop()
        for prev in reverse[pos]:
            if prev not in can_finish:
                can_finish.add(prev)
                queue.append(prev)

    if reachable - can_finish:
        return None

    states = sorted(reachable)
    index = {pos: i for i, pos in enumerate(states)}
    size = len(states)

    # m * E[pos] - sum(count[pos, dest] * E[dest]) = m
    matrix = [[0] * (size + 1) for _ in range(size)]
    for pos in states:
        i = index[pos]
        matrix[i][i] = m
        matrix[i][size] = m
        for dest, count in transitions[pos].items():
            if dest != n:
                matrix[i][index[dest]] -= count

    # Fraction-free Gaussian elimination.
    previous_pivot = 1
    for col in range(size - 1):
        if matrix[col][col] == 0:
            swap = next(
                row for row in range(col + 1, size)
                if matrix[row][col] != 0
            )
            matrix[col], matrix[swap] = matrix[swap], matrix[col]

        pivot = matrix[col][col]
        for row in range(col + 1, size):
            factor = matrix[row][col]
            for j in range(col + 1, size + 1):
                value = matrix[row][j] * pivot - factor * matrix[col][j]
                matrix[row][j] = value // previous_pivot
            matrix[row][col] = 0
        previous_pivot = pivot

    solution = [Fraction(0) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        value = Fraction(matrix[i][size])
        for j in range(i + 1, size):
            value -= matrix[i][j] * solution[j]
        solution[i] = value / matrix[i][i]

    answer = solution[index[0]]
    return [answer.numerator, answer.denominator]
