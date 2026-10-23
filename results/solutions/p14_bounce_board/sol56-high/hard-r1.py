from fractions import Fraction

def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    transitions = [[] for _ in range(n)]
    reverse = [[] for _ in range(n + 1)]

    for cell in range(n):
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            destination = resolve(landing)
            transitions[cell].append(destination)
            reverse[destination].append(cell)

    reachable = {0}
    stack = [0]
    while stack:
        cell = stack.pop()
        if cell == n:
            continue
        for destination in transitions[cell]:
            if destination not in reachable:
                reachable.add(destination)
                stack.append(destination)

    can_finish = {n}
    stack = [n]
    while stack:
        cell = stack.pop()
        for predecessor in reverse[cell]:
            if predecessor not in can_finish:
                can_finish.add(predecessor)
                stack.append(predecessor)

    if any(cell not in can_finish for cell in reachable):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # Integer system: m*E[cell] - sum(E[next]) = m.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for cell in states:
        row = index[cell]
        matrix[row][row] = m
        matrix[row][size] = m
        for destination in transitions[cell]:
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
            matrix[column], matrix[pivot_row] = matrix[pivot_row], matrix[column]

        pivot = matrix[column][column]
        for row in range(column + 1, size):
            factor = matrix[row][column]
            for j in range(column + 1, size + 1):
                matrix[row][j] = (
                    matrix[row][j] * pivot
                    - factor * matrix[column][j]
                ) // previous_pivot
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
