"""Appendix arm G (exploratory, post hoc): build with luna, repair only when worked examples fail (plus two always-review configs, one of them arm E rerun from code).

Uses the same seven problems and repeats 1-5 as the luna rescue arms (analysis/luna_rescue.py). The two luna-high
configs share their build calls; failed visible examples trigger a Haiku repair or a luna-high retry. Calls are cached
in cache/gated_repair/; graded rows replace only arm G in results/appendix/luna_rescue.jsonl.

python3 -m bench.gated_repair       # make missing calls, grade, rewrite this arm's rows"""
import hashlib, json, os, shutil, statistics, tempfile
from concurrent.futures import ThreadPoolExecutor

from analysis.luna_rescue import PIDS
from analysis.summarize import cost, usd, money
from bench import problems
from bench.grade import _norm, grade_text, run_sandbox
from bench.grade_all import extract
from bench.run import CLAUDE_FLAGS, CODEX_FLAGS, ROOT, call_claude, call_codex, cli_version, codex_flags, prompt_for

CACHE = os.path.join(ROOT, "cache", "gated_repair")
OUT = os.path.join(ROOT, "results", "appendix", "luna_rescue.jsonl")
REPS = range(1, 6)
CONFIGS = {
    "luna-high-bare+haiku-on-fail": ("gpt-6-luna", "high", codex_flags("luna-low-bare"), "haiku"),
    "luna-high-bare+retry-on-fail": ("gpt-6-luna", "high", codex_flags("luna-low-bare"), "retry"),
    "luna-low+haiku-on-fail": ("gpt-6-luna", "low", CODEX_FLAGS, "haiku"),
    "luna-high-bare+haiku-review-all": ("gpt-6-luna", "high", codex_flags("luna-low-bare"), "review"),
    "luna-low+haiku-review-all": ("gpt-6-luna", "low", CODEX_FLAGS, "review"),
    "astra-medium+haiku-on-fail": ("gpt-6-astra", "medium", CODEX_FLAGS, "haiku"),  # 2026-10-23, operator's proposed default
    "sol61-high+haiku-on-fail": ("gpt-6.1-sol", "high", CODEX_FLAGS, "haiku"),
}
REPAIR = """{prompt}

A first attempt is below. It fails these worked examples from the statement:
{report}

```python
{code}
```
Fix it. Reply with the complete corrected function in one python code block."""

# Arm E's always-on review, rebuilt for the luna-high build (E's own prompt was not kept).
REVIEW = """{prompt}

A first attempt is below. Check it against the statement and its worked examples. If it is wrong, fix it.

```python
{code}
```
Reply with the complete function, corrected or unchanged, in one python code block."""


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
    os.makedirs(CACHE, exist_ok=True); json.dump(res, open(fp + ".tmp", "w"), indent=1); os.replace(fp + ".tmp", fp)
    return res


def visible(pid, code):
    """Run the problem's worked examples in the sandbox and report visible failures."""
    if not code.strip():
        return False, "no code"
    m = problems.load(pid)
    src_path = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, prefix="visible-")
    try:
        src_path.write(code); src_path.close()
        cases = [list(args) for args, _ in m.EXAMPLES]
        results, status = run_sandbox(src_path.name, m.FUNC, cases, wall_s=10)
    finally:
        src_path.close()
        os.remove(src_path.name)
    if status != "ok":
        return False, status
    failures = []
    for (args, expected), result in zip(m.EXAMPLES, results):
        call = f"{m.FUNC}({', '.join(repr(x) for x in args)})"
        if "err" in result:
            failures.append(f"{call} returned crash: {result['err']}, expected {_norm(expected)}")
        elif _norm(result.get("out")) != _norm(expected):
            failures.append(f"{call} returned {result.get('out')!r}, expected {expected!r}")
    if len(results) != len(m.EXAMPLES):
        failures.append(f"sandbox returned {len(results)} results, expected {len(m.EXAMPLES)}")
    return not failures, "\n".join(failures)


def build_key(pid, rep, mid, effort, flags):
    p = prompt_for(pid)
    blob = {"codex_home": "isolated", "model": mid, "effort": effort, "cli": cli_version("codex"), "flags": flags,
            "prompt": p, "repeat": rep}
    return blob, p


def build(pid, rep, mid, effort, flags):
    blob, p = build_key(pid, rep, mid, effort, flags)
    return cached("build", blob, lambda cwd: call_codex(mid, effort, p, cwd, flags))


def repair_call(kind, pid, rep, prompt, code, report, mid, effort, flags):
    p = (REVIEW if kind == "review" else REPAIR).format(prompt=prompt, report=report, code=code)
    if kind in ("haiku", "review"):
        cli, model = "claude", "claude-haiku-5-5"
        blob = {"model": (model, "low"), "cli": cli_version(cli), "flags": CLAUDE_FLAGS,
                "prompt": p, "repeat": rep}
        return cached("repair", blob, lambda cwd: call_claude(model, "low", p, cwd))
    blob = {"codex_home": "isolated", "model": mid, "effort": effort, "cli": cli_version("codex"), "flags": flags,
            "prompt": p, "repeat": rep}
    return cached("repair", blob, lambda cwd: call_codex(mid, effort, p, cwd, flags))


def main():
    jobs = [(pid, rep) for rep in REPS for pid in PIDS]
    build_jobs = {}
    for cfg, (mid, effort, flags, _) in CONFIGS.items():
        for pid, rep in jobs:
            blob, _ = build_key(pid, rep, mid, effort, flags)
            key = hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()
            build_jobs.setdefault(key, (pid, rep, mid, effort, flags))
    build_items = list(build_jobs.items())
    with ThreadPoolExecutor(4) as ex:
        built = dict(zip((key for key, _ in build_items),
                         ex.map(lambda item: build(*item[1]), build_items)))

    pending, rows = [], []
    for cfg, (mid, effort, flags, repair_kind) in CONFIGS.items():
        for pid, rep in jobs:
            blob, prompt = build_key(pid, rep, mid, effort, flags)
            key = hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()
            b = built[key]; code = extract(b.get("text"))
            ok, report = visible(pid, code)
            if not ok or repair_kind == "review":
                pending.append((cfg, pid, rep, mid, effort, flags, repair_kind, prompt, code, report, b))
            else:
                rows.append((cfg, pid, rep, mid, effort, flags, b, code, ok, False, None))
    with ThreadPoolExecutor(4) as ex:
        repair_results = list(ex.map(lambda t: repair_call(t[6], t[1], t[2], t[7], t[8], t[9], t[3], t[4], t[5]), pending))
    for t, rb in zip(pending, repair_results):
        cfg, pid, rep, mid, effort, flags, _, _, _, _, b = t
        code = extract(rb.get("text"))
        rows.append((cfg, pid, rep, mid, effort, flags, b, code, visible(pid, extract(b.get("text")))[0], True, rb))

    output_rows = []
    for cfg, pid, rep, mid, effort, flags, b, code, build_ok, did_repair, rb in rows:
        g = grade_text(pid, code) if code.strip() else {"outcome": "harness_error" if (rb or b)["is_error"] else "no_code"}
        build_cost = cost({"cli": "codex", "model": mid, **b})
        repair_cost = rb.get("cost_usd") if rb and CONFIGS[cfg][3] != "retry" else (cost({"cli": "codex", "model": mid, **rb}) if rb else 0.0)
        calls = [b] + ([rb] if rb else [])
        output_rows.append({"arm": "G", "config": cfg, "problem": pid, "repeat": rep,
                            "in_tok": sum(c.get("in_tok") or 0 for c in calls),
                            "cached_tok": sum(c.get("cached_tok") or 0 for c in calls),
                            "out_tok": sum(c.get("out_tok") or 0 for c in calls),
                            "reasoning_tok": sum(c.get("reasoning_tok") or 0 for c in calls),
                            "wall_s": round(sum(c.get("wall_s") or 0 for c in calls), 2),
                            "cost_usd": usd([build_cost, repair_cost], digits=None), "passed": g["outcome"] == "pass", "check": g["outcome"],
                            "build_passed_visible": build_ok, "repaired": did_repair,
                            "build_cost_usd": build_cost, "repair_cost_usd": repair_cost,
                            "claude_cli": cli_version("claude"), "codex_cli": cli_version("codex")})
    keep = [line for line in open(OUT) if json.loads(line)["arm"] != "G"]
    with open(OUT, "w") as f:
        f.writelines(keep); f.writelines(json.dumps(r) + "\n" for r in output_rows)
    for cfg in CONFIGS:
        rr = [r for r in output_rows if r["config"] == cfg]
        passed = sum(r["passed"] for r in rr)
        print(f"{cfg}: {passed}/{len(rr)}, {money(usd((r['cost_usd'] for r in rr), passed))} USD per pass, "
              f"median {statistics.median(r['wall_s'] for r in rr):.2f}s, repairs {sum(r['repaired'] for r in rr)}")


if __name__ == "__main__":
    main()
