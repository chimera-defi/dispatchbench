from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}
    resolved = {}

    def resolve(cell: int) -> int:
        if cell in resolved:
            return resolved[cell]

        path = []
        while cell in jump:
            if cell in resolved:
                cell = resolved[cell]
                break
            path.append(cell)
            cell = jump[cell]

        for start in path:
            resolved[start] = cell
        return cell

    transitions = {}

    def destinations(cell: int) -> tuple[int, ...]:
        if cell not in transitions:
            result = []
            for roll in range(1, m + 1):
                landing = cell + roll
                if landing > n:
                    landing = 2 * n - landing
                result.append(resolve(landing))
            transitions[cell] = tuple(result)
        return transitions[cell]

    reachable = {0}
    stack = [0]

    while stack:
        cell = stack.pop()
        if cell == n:
            continue
        for destination in destinations(cell):
            if destination not in reachable:
                reachable.add(destination)
                stack.append(destination)

    if n not in reachable:
        return None

    reverse_edges = {cell: set() for cell in reachable}
    for cell in reachable:
        if cell == n:
            continue
        for destination in destinations(cell):
            reverse_edges[destination].add(cell)

    can_reach_end = {n}
    stack = [n]

    while stack:
        cell = stack.pop()
        for predecessor in reverse_edges[cell]:
            if predecessor not in can_reach_end:
                can_reach_end.add(predecessor)
                stack.append(predecessor)

    if can_reach_end != reachable:
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # Integer system:
    # m * E[cell] - sum(E[destination]) = m
    matrix = [[0] * (size + 1) for _ in range(size)]

    for cell in states:
        row = index[cell]
        matrix[row][row] = m
        matrix[row][size] = m

        for destination in destinations(cell):
            if destination != n:
                matrix[row][index[destination]] -= 1

    # Fraction-free Bareiss elimination.
    previous_pivot = 1
    for column in range(size - 1):
        pivot_row = next(
            row for row in range(column, size)
            if matrix[row][column] != 0
        )
        if pivot_row != column:
            matrix[column], matrix[pivot_row] = (
                matrix[pivot_row],
                matrix[column],
            )

        pivot = matrix[column][column]

        for row in range(column + 1, size):
            multiplier = matrix[row][column]
            for j in range(column + 1, size + 1):
                numerator = (
                    matrix[row][j] * pivot
                    - multiplier * matrix[column][j]
                )
                matrix[row][j] = numerator // previous_pivot
            matrix[row][column] = 0

        previous_pivot = pivot

    solution = [Fraction(0) for _ in range(size)]

    for row in range(size - 1, -1, -1):
        value = Fraction(matrix[row][size])
        for column in range(row + 1, size):
            value -= matrix[row][column] * solution[column]
        solution[row] = value / matrix[row][row]

    answer = solution[index[0]]
    return [answer.numerator, answer.denominator]
