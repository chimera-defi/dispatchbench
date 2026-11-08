"""Harness-family bias analysis (pre-registered): paired bootstrap helpers kept for the page's harness comparison.
results/appendix/harness_bias.{jsonl,md} are recorded outputs; the old runner that wrote them is at commit
7e946a6. Nothing here reads or writes results/."""
import random

PROBS = ["p03_ledger", "p04_taller_within", "p08_recur", "p09_k_machine_schedule", "p11_best_average", "p12_sheet"]
CFGS = ["luna-low", "haiku-low"]
REPS = range(11, 21)  # 10 fresh repeats, as pre-registered


def boot(cells, fn, n=10000, seed=1):
    """cells: {problem: {(harness,cfg): [values by repeat]}} paired; fn(per-problem list of paired tuples)->stat"""
    rng = random.Random(seed)
    probs = list(cells)
    out = []
    for _ in range(n):
        tot = []
        for p in probs:
            pairs = cells[p]
            tot.extend(pairs[rng.randrange(len(pairs))] for _ in pairs)
        out.append(fn(tot))
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n) - 1]


def paired_cells(rows):
    """Complete problem/repeat pairs in the pre-registered cell order; no grading or writes."""
    idx = {(r["harness"], r["config"], r["problem"], r["repeat"]): r for r in rows}
    H = ["claude-one-shot", "codex-tool-loop"]
    cells = {}
    missing = 0
    for p in PROBS:
        lst = []
        for rep in REPS:
            ks = [(h, c, p, rep) for c in CFGS for h in H]
            if all(k in idx for k in ks):
                lst.append(tuple(idx[k] for k in ks))  # order: luna-C, luna-X, haiku-C, haiku-X
            else:
                missing += 1
        cells[p] = lst
    return cells, missing


def interaction(tot, f=lambda r: float(r["passed"])):
    """Change in the luna-minus-Haiku gap from Claude's harness to Codex's."""
    n = len(tot)
    a = [sum(f(t[i]) for t in tot) / n for i in range(4)]
    return (a[1] - a[0]) - (a[3] - a[2])


def pass_summary(rows):
    """Read-only pass comparison using the appendix's paired bootstrap method."""
    cells, missing = paired_cells(rows)
    flat = [t for p in PROBS for t in cells[p]]
    if not flat:
        raise ValueError("harness comparison has no complete pairs")
    return dict(diff=interaction(flat), ci=boot(cells, interaction), missing=missing)

