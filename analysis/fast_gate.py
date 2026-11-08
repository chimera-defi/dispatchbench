"""Replay statement examples from cached answers; never call a model or write results.

The pipeline can equal its builder only if every cached sample check passed.
The separate fast-mode control repeats are checked, but excluded from the main
ladder and rescue metrics, just as in summarize and luna_rescue.
"""
import functools
import json
from pathlib import Path
import os
import statistics
import tempfile

from analysis.luna_rescue import PIDS
from analysis.summarize import cost
from bench import problems
from bench.grade import _norm, run_sandbox
from bench.grade_all import extract

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ("sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast")


def _metrics(rows):
    k = sum(r["passed"] for r in rows)
    return {"passes": k, "n": len(rows),
            "usd_per_pass": sum(cost(r) for r in rows) / k if k else None,
            "median_s": statistics.median(r["wall_s"] for r in rows),
            "claude_usd_per_pass": 0.0}


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


@functools.lru_cache(maxsize=1)
def summary():
    rows = [json.loads(line) for line in (ROOT / "results/2026-10-22b-function.jsonl").read_text().splitlines()]
    out = {}
    for config in CONFIGS:
        rr = [r for r in rows if r["config"] == config]
        checks = {}
        for r in rr:
            cached = json.loads((ROOT / "cache/calls" / (r["key"] + ".json")).read_text())
            checks[r["key"]] = visible(r["problem"], extract(cached.get("text")))[0]
        failures = sum(not checks[r["key"]] for r in rr)
        main = [r for r in rr if r["phase"] in ("exploratory", "fastmode")
                and 1 <= r["repeat"] <= 5 and 1 <= int(r["problem"][1:3]) <= 12]
        groups = {"all": rr, "main": main,
                  "hard": [r for r in rr if r["phase"] == "hard"],
                  "rescue": [r for r in main if r["problem"] in PIDS]}
        out[config] = {}
        for name, group in groups.items():
            failed = sum(not checks[r["key"]] for r in group)
            out[config][name] = {"n": len(group), "failures": failed,
                                 "pipeline": _metrics(group) if not failures and group else None,
                                 "status": "derived: check never failed" if not failures else
                                 "would need a Haiku call; pipeline was not run"}
    return out
