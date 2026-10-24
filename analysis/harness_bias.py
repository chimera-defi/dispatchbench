"""Harness-family bias analysis (pre-registered). Usage: python3 -m analysis.harness_bias
Reads fresh repeats (11-20): Claude harness from cache/calls (phase harness_bias), graded here;
Codex harness from results/appendix/codex_harness.jsonl. Writes results/appendix/harness_bias.{jsonl,md}.
Does not touch results/2026-10-22b-function.jsonl (only reads it for a drift check)."""
import hashlib, json, math, os, random, statistics as st
from collections import defaultdict
from bench import problems
from bench.grade import grade_text
from bench.grade_all import extract, GRADES, FIELDS
from bench.run import CALLS, ROOT

PROBS = ["p03_ledger", "p04_taller_within", "p08_recur", "p09_k_machine_schedule", "p11_best_average", "p12_sheet"]
CFGS = ["luna-low", "haiku-low"]
REPS = range(11, 14)  # scope cut by operator: 3 repeats (was 10)
OUT = os.path.join(ROOT, "results", "appendix")


PRICES = json.load(open(os.path.join(ROOT, "results", "prices.json")))["models"]


def fill_cost(r):
    """Codex-model rows have no measured cost: list-price proxy from tokens (in_tok includes cached)."""
    if r.get("cost_usd") is None and r.get("model") in PRICES and r.get("in_tok") is not None:
        pr = PRICES[r["model"]]; c = r.get("cached_tok") or 0
        r["cost_usd"] = ((r["in_tok"] - c) * pr["input"] + c * pr["cached_input"] + (r.get("out_tok") or 0) * pr["output"]) / 1e6
        r["cost_kind"] = "proxy (list price x tokens)"
    return r


def claude_rows():
    rows = []
    for f in sorted(os.listdir(CALLS)):
        e = json.load(open(os.path.join(CALLS, f)))
        if e.get("phase") != "harness_bias" or e["repeat"] not in REPS:
            continue
        code = extract(e.get("text"))
        ph = hashlib.sha256(open(problems.path(e["problem"]), "rb").read()).hexdigest()[:16]
        gp = os.path.join(GRADES, hashlib.sha256((ph + "\0" + code).encode()).hexdigest() + ".json")
        if e["is_error"] and not code.strip():
            g = {"outcome": "harness_error", "detail": (e.get("error") or "")[:300]}
        elif os.path.exists(gp):
            g = json.load(open(gp))
        else:
            g = grade_text(e["problem"], code) if code.strip() else {"outcome": "no_code", "detail": "empty completion"}
            json.dump(g, open(gp, "w"))
        r = {k: e.get(k) for k in FIELDS}
        r.update(outcome=g["outcome"], passed=g["outcome"] == "pass", grade_detail=g.get("detail"), harness="claude-one-shot")
        rows.append(r)
    return rows


def codex_rows():
    rows = []
    for l in open(os.path.join(OUT, "codex_harness.jsonl")):
        r = json.loads(l)
        if r["repeat"] in REPS and r["problem"] in PROBS and r["config"] in CFGS:
            r["harness"] = "codex-tool-loop"
            rows.append(r)
    return rows


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


def main():
    rows = [fill_cost(r) for r in claude_rows() + codex_rows()]
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "harness_bias.jsonl"), "w") as f:
        for r in sorted(rows, key=lambda r: (r["harness"], r["config"], r["problem"], r["repeat"])):
            f.write(json.dumps(r) + "\n")
    cells, missing = paired_cells(rows)
    H = ["claude-one-shot", "codex-tool-loop"]

    def logf(key):
        return lambda r: math.log(max(r[key] or 1e-9, 1e-9))

    flat = [t for p in PROBS for t in cells[p]]
    res = {}
    res["pass"] = (interaction(flat), boot(cells, interaction))
    for name, key in [("log_cost", "cost_usd"), ("log_wall", "wall_s")]:
        fn = lambda tot, f=logf(key): interaction(tot, f)
        res[name] = (fn(flat), boot(cells, fn))
    errs = {f"{h}/{c}": sum(1 for r in rows if r["harness"] == h and r["config"] == c and r["outcome"] == "harness_error") for h in H for c in CFGS}
    cellstat = {}
    for h in H:
        for c in CFGS:
            rs = [r for r in rows if r["harness"] == h and r["config"] == c]
            cellstat[(h, c)] = (sum(r["passed"] for r in rs), len(rs), sum(r["cost_usd"] or 0 for r in rs),
                                st.median(r["wall_s"] for r in rs) if rs else float("nan"))
    nocost = sum(1 for r in rows if r["cost_usd"] is None)
    # drift check: old 10-22 rows, repeats 1-5, claude harness
    old = defaultdict(lambda: [0, 0])
    for l in open(os.path.join(ROOT, "results", "2026-10-22b-function.jsonl")):
        r = json.loads(l)
        if r["phase"] == "main" and r["config"] in CFGS and r["problem"] in PROBS:
            old[r["config"]][0] += r["passed"]; old[r["config"]][1] += 1
    d, (lo, hi) = res["pass"]
    if lo > 0 and d > 0 and d >= 0.15:
        verdict = "YES: harness family biases results (CI excludes 0, D > 0, D >= 0.15)."
    elif lo <= 0 <= hi:
        verdict = "NO bias of about 0.3 or more is detectable (CI contains 0). This is not 'no bias'."
    else:
        verdict = "NOT 'yes' under the rule (CI excludes 0 but D fails the D > 0 and D >= 0.15 test)."
    cx = [k for k in ("log_cost", "log_wall") if not (res[k][1][0] <= 0 <= res[k][1][1])]
    note = ("A secondary hit (" + ", ".join(cx) + ") means the harness changes cost/latency rankings, not bias.") if cx else "No secondary (cost/time) interaction excludes 0."

    def cell(h, c):
        p, n, cost, w = cellstat[(h, c)]
        return f"{p}/{n} pass, ${cost:.3f}, {w:.1f}s"
    md = f"""# Does the harness family bias results? (underpowered subset, n=18 per cell)

**Answer: {verdict}**

D = {d:+.3f}, 95% CI [{lo:+.3f}, {hi:+.3f}]  (D>0 would mean Codex harness favours Codex model).

| | Claude harness (one-shot) | Codex harness (tool loop) |
|---|---|---|
| luna-low (Codex family) | {cell(H[0], 'luna-low')} | {cell(H[1], 'luna-low')} |
| haiku-low (Claude family) | {cell(H[0], 'haiku-low')} | {cell(H[1], 'haiku-low')} |

Cells: pass count / calls, total $, median wall seconds. 6 problems x 3 fresh repeats (11-13) per cell, n=18 per cell, 72 calls. Scope cut from the pre-registered 10 repeats; treat as underpowered subset.
`harness_error` rows: {sum(errs.values())} ({errs}); counted as fails above.
Calls with no cost figure: {nocost}. Incomplete pairs dropped: {missing}.

Secondary (interaction on mean log): cost D = {res['log_cost'][0]:+.3f} CI [{res['log_cost'][1][0]:+.3f}, {res['log_cost'][1][1]:+.3f}]; wall D = {res['log_wall'][0]:+.3f} CI [{res['log_wall'][1][0]:+.3f}, {res['log_wall'][1][1]:+.3f}]. {note}
Note: Codex-model $ is a list-price proxy, Claude-model $ is measured, in both harnesses.

Drift check (10-22 Claude-harness rows, 6 problems x 5 repeats): luna-low {old['luna-low'][0]}/{old['luna-low'][1]}, haiku-low {old['haiku-low'][0]}/{old['haiku-low'][1]} pass.

**Confound:** the harnesses differ in mechanism (one-shot vs tool loop with code execution), not just in who wrote them. A positive D could be mechanism x model, not family loyalty. The prompt-swap ablation within each style runs only if D is positive.

Method: pairs by (problem, repeat); bootstrap 10,000 resamples of pairs stratified by problem, 95% percentile CI; seed 1.

Reproduce:
```
P=p03_ledger,p04_taller_within,p08_recur,p09_k_machine_schedule,p11_best_average,p12_sheet
for r in 11 12 13; do
  python3 -m bench.run --phase harness_bias --configs luna-low,haiku-low --problems $P --repeats $r --lanes 2 &
  python3 -m bench.codex_harness --configs luna-low,haiku-low --problems $P --repeats $r --lanes 2
  wait
done
python3 -m analysis.harness_bias
```
"""
    open(os.path.join(OUT, "harness_bias.md"), "w").write(md)
    print(md)


if __name__ == "__main__":
    main()
