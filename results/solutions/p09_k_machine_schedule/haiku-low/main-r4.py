def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    # Process jobs by start time. A state is the sorted tuple of machine
    # free times, where any machine free by the current start is stored as 0.
    jobs = sorted(jobs, key=lambda j: (j[0], j[1]))
    states = {tuple([0] * k): 0}

    for s, e, p in jobs:
        new_states = dict(states)  # option: skip this job
        for busy, val in states.items():
            tried = set()
            for t in busy:
                # Machine must be free at or before start; identical free times are tried once
                if t > s or t in tried:
                    continue
                tried.add(t)
                lst = list(busy)
                lst[lst.index(t)] = e
                # Machines free by s are equivalent for all later jobs (starts >= s)
                norm = tuple(sorted(0 if x <= s else x for x in lst))
                nv = val + p
                if new_states.get(norm, -1) < nv:
                    new_states[norm] = nv
        states = new_states

    return max(states.values())
