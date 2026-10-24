"""Offline review evidence. No model calls; all writes go to temp dirs or --output.

PYTHONDONTWRITEBYTECODE=1 python3 -m bench.review_probe --output results/review-astra/probe.json
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from unittest.mock import patch

from bench import run as R
from bench.agentic import run as A
from bench import gated_repair as G
from analysis.summarize import cost, cost_uncached, load

ROOT = Path(R.ROOT)


def data_evidence():
    functions = load(ROOT / "results/2026-10-22b-function.jsonl")
    agents = load(ROOT / "results/2026-10-22b-agentic.jsonl")
    appendix = load(ROOT / "results/appendix/luna_rescue.jsonl")
    tests = json.loads((ROOT / "results/agentic_tests.json").read_text())
    summary = {}
    for cfg in sorted({r["config"] for r in agents}):
        rows = [r for r in agents if r["config"] == cfg]
        traces = 0
        invocations = []
        tool_sets = []
        for row in rows:
            path = ROOT / "cache/agentic_raw" / f"agentic-{row['key']}.out"
            if not path.exists():
                continue
            traces += 1
            for no, line in enumerate(path.read_text().splitlines(), 1):
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("type") == "system" and ev.get("subtype") == "init":
                    tools = ev.get("tools", [])
                    if tools not in tool_sets:
                        tool_sets.append(tools)
                item = ev.get("item") or {}
                if ev.get("type") == "item.completed" and "kimi-delegate --task" in item.get("command", ""):
                    invocations.append({"source": f"{path.relative_to(ROOT)}:{no}",
                                        "auth_failed": "auth/session error" in item.get("aggregated_output", "")})
        summary[cfg] = {
            "n": len(rows), "hidden_pass": sum(r["hidden_pass"] for r in rows),
            "visible_pass": sum(r["visible_pass"] for r in rows),
            "full_contract_pass": sum(r["hidden_pass"] and r["visible_pass"] and r["own_tests"]
                                      and not r["tests_tampered"] and not r["is_error"] for r in rows),
            "transcripts": traces, "test_count_rows": sum(r["config"] == cfg for r in tests),
            "claude_tool_sets": tool_sets, "actual_kimi_invocations": invocations,
        }
    costs = {}
    for cfg in ("haiku-low", "haiku-high", "sol61-high", "astra-medium", "luna-low-bare"):
        rows = [r for r in functions if r["config"] == cfg and r["phase"] in ("main", "exploratory")]
        passes = sum(r["passed"] for r in rows)
        costs[cfg] = {"passes": passes, "n": len(rows), "usd_per_pass": sum(map(cost, rows)) / passes,
                      "codex_no_cache_sensitivity": sum(map(cost_uncached, rows)) / passes,
                      "cache_token_share": sum(r["cached_tok"] for r in rows) / sum(r["in_tok"] for r in rows)}
    measured = {}
    for name in ("calls", "agentic", "trim", "plan_first", "gated_repair"):
        measured[name] = sum(json.loads(p.read_text()).get("cost_usd") or 0
                             for p in (ROOT / "cache" / name).glob("*.json"))
    pipelines = {}
    for cfg in sorted({r["config"] for r in appendix if r["arm"] == "G"}):
        rows = [r for r in appendix if r["arm"] == "G" and r["config"] == cfg]
        pipelines[cfg] = {"n": len(rows), "passes": sum(r["passed"] for r in rows),
                          "repairs": sum(r["repaired"] for r in rows),
                          "failures_not_repaired": sum(not r["passed"] and not r["repaired"] for r in rows)}
    return {"function_rows": len(functions),
            "codex_function_tool_items": sum(r.get("tool_items") or 0 for r in functions if r["cli"] == "codex"),
            "agentic": summary, "function_costs": costs, "pipeline_G": pipelines,
            "measured_cache_costs": measured,
            "reported_claude_total": json.loads((ROOT / "results/summary.json").read_text())["spend"]["claude_measured_usd"],
            "failed_visible_runs": [{k: r[k] for k in ("config", "task", "repeat", "key", "visible", "hidden")}
                                    for r in agents if not r["visible_pass"]]}


def mocked_lifecycle():
    """Exercise the real runner paths with fake completions and temporary caches."""
    result = {}
    with tempfile.TemporaryDirectory(prefix="mrb-review-") as tmp:
        calls, raw = Path(tmp) / "calls", Path(tmp) / "raw"
        fake = {"wall_s": 1, "text": "", "is_error": True, "error": "temporary service error", "cost_usd": .01}
        with patch.object(R, "CALLS", str(calls)), patch.object(R, "RAW", str(raw)), \
             patch.object(R, "cli_version", return_value="test-version"), \
             patch.object(R, "call_claude", return_value=(fake, "")) as call:
            first = R.one("haiku-low", "p01_overlap_minutes", 1, "review", 1)
            second = R.one("haiku-low", "p01_overlap_minutes", 1, "review", 1)
            result["transient_error"] = {"first": first, "second": second, "provider_calls": call.call_count}
            with patch.object(R, "call_claude", side_effect=subprocess.TimeoutExpired("fake", 1200)):
                try:
                    R.one("haiku-low", "p01_overlap_minutes", 2, "review", 1)
                except subprocess.TimeoutExpired:
                    result["timeout"] = {"escaped": True, "ledger_entries": len(list(calls.glob("*.json"))),
                                         "accounted_usd": R.claude_spend()}
        with patch.object(R, "one", return_value="ERR quota exceeded") as call, \
             patch.object(R, "claude_spend", return_value=0), \
             patch("sys.argv", ["bench.run", "--phase", "review", "--configs", "luna-low", "--problems",
                                "p01_overlap_minutes", "--repeats", "1-2", "--lanes", "1"]), \
             contextlib.redirect_stdout(io.StringIO()):
            R.main()
            result["quota_lane_provider_attempts"] = call.call_count
        with patch.object(G, "CACHE", str(Path(tmp) / "gated")), \
             patch.object(G, "cli_version", return_value="test-version"), \
             patch.object(R, "CALLS", str(Path(tmp) / "empty-calls")), \
             patch.object(R, "CLAUDE_BUDGET_USD", 0), \
             patch.object(G, "call_claude", return_value=({"cost_usd": .02}, "")) as call:
            G.repair_call("haiku", "p01_overlap_minutes", 1, "prompt", "code", "failed", "unused", "low", [])
            result["gated_repair_with_zero_budget"] = {"provider_calls": call.call_count,
                                                       "run_claude_spend_usd": R.claude_spend()}
        repo, hidden = Path(tmp) / "repo", Path(tmp) / "hidden"
        repo.mkdir(); hidden.mkdir()
        (repo / "a.py").write_text("x = 1\n")
        before = A.tree_hash(repo, hidden)
        (repo / "__pycache__").mkdir()
        (repo / "__pycache__/a.pyc").write_bytes(b"irrelevant generated bytecode")
        result["bytecode_changes_task_cache_key"] = before != A.tree_hash(repo, hidden)
    assert result["transient_error"]["provider_calls"] == 1
    assert result["timeout"]["escaped"]
    assert result["quota_lane_provider_attempts"] == 2
    assert result["gated_repair_with_zero_budget"]["provider_calls"] == 1
    return result


def skip_grading_probe():
    """A broken starter can earn hidden_pass by adding a pytest skip hook.

    No model is invoked. Existing tests and package code are never changed.
    """
    with tempfile.TemporaryDirectory(prefix="mrb-review-") as tmp:
        base = Path(tmp)
        starter = base / "starter"
        task = ROOT / "bench/agentic/tasks/t2_cache_bugs"
        shutil.copytree(task / "repo", starter)
        shutil.copy(task / "hidden/test_hidden.py", starter / "tests/test_hidden.py")
        before = A.pytest(str(starter), "tests/test_hidden.py")

        def fake_model(mid, effort, prompt, work):
            w = Path(work)
            (w / "conftest.py").write_text("import pytest\ndef pytest_collection_modifyitems(items):\n"
                                           "    for item in items:\n"
                                           "        item.add_marker(pytest.mark.skip(reason='review probe'))\n")
            (w / "tests/test_regressions.py").write_text("# empty regression file\n")
            return {"is_error": False, "error": None}, ""

        cache = base / "agent-cache"
        with patch.object(A, "CACHE", str(cache)), patch.object(A, "RAW", str(base / "raw")), \
             patch.object(A, "cli_version", return_value="test-version"), \
             patch.object(A, "run_codex", side_effect=fake_model):
            A.one("luna-low", "t2_cache_bugs", 987, 1)
        row = json.loads(next(cache.glob("*.json")).read_text())
        result = {"unmodified_starter_hidden": before,
                  "with_skip_hook": {k: row[k] for k in ("visible", "hidden", "visible_pass", "hidden_pass", "own_tests", "tests_tampered")}}
        assert not before["ok"] and before["failed"] > 0
        assert row["hidden_pass"] and row["hidden"]["passed"] == 0
        assert row["tests_tampered"] == [] and row["own_tests"]
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Restrict durable outputs to this review; never overwrite existing result sets.
    args.output.resolve().relative_to((ROOT / "results/review-astra").resolve())
    evidence = {"model_calls": 0, "claude_spend_usd": 0,
                "data": data_evidence(), "lifecycle": mocked_lifecycle(), "grading": skip_grading_probe()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Offline probes verified; evidence: {args.output}")


if __name__ == "__main__":
    main()
