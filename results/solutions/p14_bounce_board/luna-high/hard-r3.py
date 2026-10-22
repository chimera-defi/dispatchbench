from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    states = [cell for cell in range(n) if cell not in jump]
    transitions = {}

    for cell in states:
        counts = {}
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            landing = resolve(landing)
            counts[landing] = counts.get(landing, 0) + 1
        transitions[cell] = counts

    # Find states reachable from 0.
    reachable = set()
    stack = [0]
    while stack:
        cell = stack.pop()
        if cell in reachable:
            continue
        reachable.add(cell)
        for landing in transitions[cell]:
            if landing != n and landing not in reachable:
                stack.append(landing)

    # Find states from which the terminal cell is reachable.
    reverse = {cell: [] for cell in states}
    can_finish = set()
    for cell in states:
        for landing in transitions[cell]:
            if landing == n:
                can_finish.add(cell)
            else:
                reverse[landing].append(cell)

    stack = list(can_finish)
    while stack:
        cell = stack.pop()
        for prev in reverse[cell]:
            if prev not in can_finish:
                can_finish.add(prev)
                stack.append(prev)

    if any(cell not in can_finish for cell in reachable):
        return None

    ordered = sorted(reachable)
    index = {cell: i for i, cell in enumerate(ordered)}
    size = len(ordered)

    # Solve (mI - C)E = m, where C contains transition counts
    # to nonterminal states.
    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]
    for cell in ordered:
        row = index[cell]
        matrix[row][row] = Fraction(m)
        matrix[row][size] = Fraction(m)
        for landing, count in transitions[cell].items():
            if landing != n and landing in index:
                matrix[row][index[landing]] -= count

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        divisor = matrix[col][col]
        matrix[col] = [value / divisor for value in matrix[col]]

        for row in range(size):
            if row == col or not matrix[row][col]:
                continue
            factor = matrix[row][col]
            matrix[row] = [
                matrix[row][j] - factor * matrix[col][j]
                for j in range(size + 1)
            ]

    answer = matrix[index[0]][size]
    return [answer.numerator, answer.denominator]
