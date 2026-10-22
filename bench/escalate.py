"""Escalation rule from PLAN.md, step 4: if a model's highest base effort passes 2/5 or fewer on a problem, the next effort
level of that model runs 5 repeats on those problems only. One step at most.

python3 -m bench.escalate            # print the subsets
python3 -m bench.escalate --run      # run them (cached calls are skipped), at most 4 lanes"""
import argparse, json, os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from bench.run import one, claude_spend

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNC = os.path.join(ROOT, "results", "2026-10-22b-function.jsonl")
STEP = {"haiku-medium": "haiku-high", "sonnet-medium": "sonnet-high", "luna-medium": "luna-high", "sol61-medium": "sol61-high"}


def subsets():
    passes = defaultdict(int); seen = set()
    for r in map(json.loads, open(FUNC)):
        if r["phase"] == "main" and r["config"] in STEP:
            passes[(r["config"], r["problem"])] += r["passed"]; seen.add((r["config"], r["problem"]))
    out = defaultdict(list)
    for c, p in sorted(seen):
        if passes[(c, p)] <= 2: out[STEP[c]].append(p)
    return dict(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true"); a = ap.parse_args()
    sub = subsets()
    for c, ps in sub.items(): print(f"{c}: {', '.join(ps)}")
    if not sub: print("no problem at or below 2/5 for any highest base effort: no escalation")
    if not a.run or not sub: return

    def lane(c):
        for rep in range(1, 6):
            for p in sub[c]:
                msg = one(c, p, rep, "escalation", min(4, len(sub)))
                print(f"[escalation] {c} {p} r{rep}: {msg}", flush=True)
                if msg.startswith("refused"): return
    with ThreadPoolExecutor(min(4, len(sub))) as ex:
        list(ex.map(lane, sub))
    print(f"Claude spend so far: ${claude_spend():.4f}")


if __name__ == "__main__":
    main()
