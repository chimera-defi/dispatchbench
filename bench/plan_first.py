"""Appendix arm F (exploratory, post hoc): haiku-low writes a plan without code, then luna builds from it.

Same seven problems and repeats 1-5 as the luna rescue arms (analysis/luna_rescue.py). One Haiku plan per (problem,
repeat) is shared by both builders: luna-low (stock Codex harness, as in arm E) and luna-high (stripped harness, as in
arm D). Calls are cached in cache/plan_first/; graded rows are appended to results/appendix/luna_rescue.jsonl.

python3 -m bench.plan_first            # make missing calls, grade, rewrite this arm's rows"""
import hashlib, json, os, shutil, tempfile
from concurrent.futures import ThreadPoolExecutor

from analysis.luna_rescue import PIDS
from analysis.summarize import cost
from bench import problems
from bench.grade import grade_text
from bench.grade_all import extract
from bench.run import CLAUDE_FLAGS, CODEX_FLAGS, ROOT, call_claude, call_codex, cli_version, codex_flags, prompt_for

CACHE = os.path.join(ROOT, "cache", "plan_first")
OUT = os.path.join(ROOT, "results", "appendix", "luna_rescue.jsonl")
REPS = range(1, 6)
PLANNER = ("claude-haiku-5-5", "low")
BUILDERS = {"haiku-low-plan+luna-low": ("gpt-6-luna", "low", CODEX_FLAGS),
            "haiku-low-plan+luna-high-bare": ("gpt-6-luna", "high", codex_flags("luna-low-bare"))}

PLAN = """You are planning, not coding. Another model will write the code from your plan.

{statement}

The function to implement:
```python
{signature}
```
Write a short plan: the algorithm and data structures, the edge cases the examples hint at, and the time complexity
needed for the largest inputs. Do not write code."""

BUILD = """{prompt}

A reviewer wrote this plan. Follow it unless you find it wrong.

{plan}"""


def cached(kind, blob, make):
    key = hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()
    fp = os.path.join(CACHE, f"{kind}-{key}.json")
    if os.path.exists(fp):
        return json.load(open(fp))
    cwd = tempfile.mkdtemp(prefix="mrb-")
    try:
        res, _ = make(cwd)
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    os.makedirs(CACHE, exist_ok=True); json.dump(res, open(fp, "w"), indent=1)
    return res


def plan(pid, rep):
    m = problems.load(pid); p = PLAN.format(statement=m.STATEMENT.strip(), signature=m.SIGNATURE)
    blob = {"model": PLANNER, "cli": cli_version("claude"), "flags": CLAUDE_FLAGS, "prompt": p, "repeat": rep}
    return cached("plan", blob, lambda cwd: call_claude(*PLANNER, p, cwd))


def build(cfg, pid, rep, pl):
    mid, eff, flags = BUILDERS[cfg]; p = BUILD.format(prompt=prompt_for(pid), plan=pl["text"].strip())
    blob = {"config": cfg, "model": mid, "effort": eff, "cli": cli_version("codex"), "flags": flags, "prompt": p, "repeat": rep}
    return cached("build", blob, lambda cwd: call_codex(mid, eff, p, cwd, flags))


def main():
    jobs = [(pid, rep) for rep in REPS for pid in PIDS]
    with ThreadPoolExecutor(4) as ex:
        plans = dict(zip(jobs, ex.map(lambda j: plan(*j), jobs)))
    bad = [j for j, p in plans.items() if p["is_error"] or not p["text"].strip()]
    assert not bad, f"planner errors: {bad}"
    print(f"plans done; Haiku ${sum(p['cost_usd'] or 0 for p in plans.values()):.4f}", flush=True)
    with ThreadPoolExecutor(4) as ex:
        builds = dict(zip([(c, *j) for c in BUILDERS for j in jobs],
                          ex.map(lambda t: build(t[0], t[1], t[2], plans[(t[1], t[2])]), [(c, *j) for c in BUILDERS for j in jobs])))
    rows = []
    for (c, pid, rep), b in builds.items():
        pl = plans[(pid, rep)]; code = extract(b.get("text"))
        g = grade_text(pid, code) if code.strip() else {"outcome": "harness_error" if b["is_error"] else "no_code"}
        luna = cost({"cli": "codex", "model": BUILDERS[c][0], **b}); haiku = pl["cost_usd"] or 0.0
        rows.append({"arm": "F", "config": c, "problem": pid, "repeat": rep,
                     "in_tok": pl["in_tok"] + b["in_tok"], "cached_tok": pl["cached_tok"] + b["cached_tok"], "out_tok": pl["out_tok"] + b["out_tok"],
                     "reasoning_tok": pl["reasoning_tok"] + b["reasoning_tok"], "wall_s": round(pl["wall_s"] + b["wall_s"], 2),
                     "cost_usd": luna + haiku, "passed": g["outcome"] == "pass", "check": g["outcome"],
                     "luna_cost_usd": luna, "haiku_cost_usd": haiku,
                     "claude_cli": cli_version("claude"), "codex_cli": cli_version("codex")})
        print(f"{c} {pid} r{rep}: {g['outcome']}", flush=True)
    keep = [l for l in open(OUT) if json.loads(l)["arm"] != "F"]
    with open(OUT, "w") as f:
        f.writelines(keep); f.writelines(json.dumps(r) + "\n" for r in rows)
    for c in BUILDERS:
        rr = [r for r in rows if r["config"] == c]
        print(f"{c}: {sum(r['passed'] for r in rr)}/{len(rr)}, ${sum(r['cost_usd'] for r in rr) / max(1, sum(r['passed'] for r in rr)):.5f} per pass")


if __name__ == "__main__":
    main()
