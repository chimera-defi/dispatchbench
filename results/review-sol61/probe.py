"""Offline review probes. Run from repo root: python3 results/review-sol61/probe.py.

No model subprocesses, credentials, network, or writes to existing benchmark data.
Only pytest subprocesses execute; fixtures/cache writes live in temporary directories.
JSON is printed to stdout, so the caller controls the destination.
"""
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
import json
import os
import statistics
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from bench import run as R
from bench.agentic import run as A
from analysis.summarize import cost, cost_uncached
from analysis.agentic_tests import analyse
from analysis.report import tables_md


def read_rows(path):
    return [json.loads(line) for line in (ROOT / path).read_text().splitlines()]


def run():
    out = {"model_calls": 0, "new_claude_spend_usd": 0.0}
    function = read_rows("results/2026-10-22b-function.jsonl")
    agentic = read_rows("results/2026-10-22b-agentic.jsonl")
    codex = [r for r in function if r["cli"] == "codex"]
    out["function_tools"] = {"codex_calls": len(codex),
                             "nonzero_tool_items": sum(bool(r.get("tool_items")) for r in codex)}
    out["agentic"] = {
        cfg: {"runs": len(rr := [r for r in agentic if r["config"] == cfg]),
              "hidden_passes": sum(r["hidden_pass"] for r in rr),
              "minimum_hidden_tests_passed": min(r["hidden"]["passed"] for r in rr),
              "median_s": statistics.median(r["wall_s"] for r in rr),
              "raw_transcripts": sum((ROOT / "cache/agentic_raw" / f"agentic-{r['key']}.out").exists() for r in rr)}
        for cfg in sorted({r["config"] for r in agentic})}
    out["function_rates"] = {}
    for cfg in ("luna-low", "luna-medium", "luna-high", "haiku-low", "haiku-high", "sol61-high", "sonnet-medium"):
        rr = [r for r in function if r["config"] == cfg and r["phase"] in ("main", "exploratory", "escalation")]
        k = sum(r["passed"] for r in rr)
        out["function_rates"][cfg] = dict(runs=len(rr), passed=k,
            usd_per_pass=sum(map(cost, rr)) / k,
            uncached_usd_per_pass=sum(map(cost_uncached, rr)) / k,
            mean_output_tokens=sum(r["out_tok"] for r in rr) / len(rr),
            mean_reasoning_tokens=sum(r.get("reasoning_tok") or 0 for r in rr) / len(rr),
            lanes=dict(Counter(r["lanes"] for r in rr)),
            first_timestamp=min(r["ts"] for r in rr), last_timestamp=max(r["ts"] for r in rr))

    # CLI-reported costs are not independently verified invoices. Keep the CLI's provenance.
    bases = Counter()
    toolsets = Counter()
    for r in agentic:
        if r["cli"] != "claude":
            continue
        path = ROOT / "cache/agentic_raw" / f"agentic-{r['key']}.out"
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "result":
                for usage in event.get("modelUsage", {}).values():
                    bases[usage.get("costBasis", "absent")] += 1
            if event.get("subtype") == "init":
                toolsets[",".join(sorted(event.get("tools", [])))] += 1
    out["claude_recorded_cost_basis"] = dict(bases)
    out["claude_recorded_toolsets"] = dict(toolsets)

    delegation = {"cached_delegate_calls": 0, "actual_task_invocations": 0,
                  "actual_task_exit_codes": [], "shell_commands": 0, "host_marked_commands": 0}
    for r in agentic:
        if r["config"] != "sol61-medium":
            continue
        delegation["cached_delegate_calls"] += r["delegate_calls"]
        path = ROOT / "cache/agentic_raw" / f"agentic-{r['key']}.out"
        *_, shell, host = analyse(str(path))
        delegation["shell_commands"] += shell
        delegation["host_marked_commands"] += host
        for line in path.read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            item = event.get("item") or {}
            if (event.get("type") == "item.completed" and item.get("type") == "command_execution"
                    and "kimi-delegate --task" in item.get("command", "")):
                delegation["actual_task_invocations"] += 1
                delegation["actual_task_exit_codes"].append(item.get("exit_code"))
    out["sol61_medium_delegation"] = delegation

    tests_evidence = json.loads((ROOT / "results/agentic_tests.json").read_text())
    rendered = tables_md(json.loads((ROOT / "results/summary.json").read_text()))["agentic"]
    out["missing_evidence_rendered_as_zero"] = {}
    for cfg in ("haiku-high", "sol61-high", "astra-medium"):
        assert not any(r["config"] == cfg for r in tests_evidence)
        line = next(line for line in rendered.splitlines() if line.startswith(f"| {cfg} |"))
        assert line.split("|")[4].strip() == "0", line
        out["missing_evidence_rendered_as_zero"][cfg] = line

    repair_rows = read_rows("results/appendix/luna_rescue.jsonl")
    out["repair_exposure"] = {}
    for cfg in ("sol61-high+haiku-on-fail", "astra-medium+haiku-on-fail",
                "luna-high-bare+haiku-on-fail", "luna-high-bare+retry-on-fail", "luna-low+haiku-on-fail"):
        rr = [r for r in repair_rows if r["config"] == cfg]
        out["repair_exposure"][cfg] = dict(runs=len(rr), repairs=sum(r["repaired"] for r in rr),
                                          passes=sum(r["passed"] for r in rr))

    directory_costs = {}
    for directory in ("calls", "agentic", "trim", "gated_repair", "plan_first"):
        entries = [json.loads(p.read_text()) for p in (ROOT / "cache" / directory).glob("*.json")]
        directory_costs[directory] = sum(r.get("cost_usd") or 0 for r in entries)
    out["spend"] = dict(cache_measured_usd=directory_costs,
        function_guard_counts_usd=R.claude_spend(),
        agentic_guard_counts_usd=R.claude_spend() + A.agentic_spend(),
        retained_five_directory_total_usd=sum(directory_costs.values()))

    # A real, failing hidden test can be skipped by a new conftest.py without touching originals.
    with tempfile.TemporaryDirectory(prefix="mrb-review-pytest-") as tmp:
        tests = Path(tmp) / "tests"
        tests.mkdir()
        (tests / "test_zz_hidden_probe.py").write_text("def test_hidden():\n    assert False\n")
        before = A.pytest(tmp, "tests/test_zz_hidden_probe.py")
        (tests / "conftest.py").write_text(
            "import pytest\ndef pytest_collection_modifyitems(items):\n"
            "    for item in items:\n"
            "        if 'test_zz_hidden_' in str(item.fspath):\n"
            "            item.add_marker(pytest.mark.skip(reason='review probe'))\n")
        after = A.pytest(tmp, "tests/test_zz_hidden_probe.py")
        assert not before["ok"] and after["ok"] and after["passed"] == 0, (before, after)
        out["hidden_skip_bypass"] = dict(before=before, after=after)

    # Mock only version discovery: no CLI is launched. Different host contexts collide.
    with patch.object(R, "cli_version", return_value="review-fixed-version"):
        with patch.dict(os.environ, {"CODEX_HOME": "/tmp/review-context-a"}):
            first = R.key_for("sol61-high", "p01_overlap_minutes", 1, "same prompt")
        with patch.dict(os.environ, {"CODEX_HOME": "/tmp/review-context-b"}):
            second = R.key_for("sol61-high", "p01_overlap_minutes", 1, "same prompt")
        assert first == second
        out["context_cache_collision"] = dict(equal_keys=first == second, key=first)

    # Run the real lane loop with a fake quota response. All model invocations are mocked.
    quota = dict(wall_s=0.01, text="", is_error=True, error="quota exceeded", in_tok=0,
                 cached_tok=0, out_tok=0, cost_usd=None)
    with tempfile.TemporaryDirectory(prefix="mrb-review-quota-") as tmp:
        with patch.multiple(R, CALLS=str(Path(tmp) / "calls"), RAW=str(Path(tmp) / "raw")), \
             patch.object(R, "cli_version", return_value="review-fixed-version"), \
             patch.object(R, "call_codex", return_value=(quota, "fake quota")) as make, \
             patch.object(sys, "argv", ["bench.run", "--phase", "review", "--configs", "sol61-high",
                                      "--problems", "p01_overlap_minutes", "--repeats", "1-2", "--lanes", "1"]), \
             redirect_stdout(StringIO()):
            R.main()
        assert make.call_count == 2, make.call_count
        out["quota_lane"] = dict(mock_calls_after_quota=make.call_count, expected_stop_after=1)

    # The function spend reader examines an incomplete .tmp journal as if it were a finished call.
    with tempfile.TemporaryDirectory(prefix="mrb-review-ledger-") as tmp:
        (Path(tmp) / "inflight.json.tmp").write_text('{"cli":')
        with patch.object(R, "CALLS", tmp):
            try:
                R.claude_spend()
            except json.JSONDecodeError:
                out["inflight_spend_reader"] = "JSONDecodeError"
            else:
                raise AssertionError("Expected incomplete ledger file to fail")

    # Timeout in the real one() entrypoint is not turned into a ledger row or retry.
    with tempfile.TemporaryDirectory(prefix="mrb-review-timeout-") as tmp:
        with patch.multiple(R, CALLS=str(Path(tmp) / "calls"), RAW=str(Path(tmp) / "raw")), \
             patch.object(R, "cli_version", return_value="review-fixed-version"), \
             patch.object(R, "call_codex", side_effect=subprocess.TimeoutExpired("fake", 1200)):
            try:
                R.one("sol61-high", "p01_overlap_minutes", 1, "review", 1)
            except subprocess.TimeoutExpired:
                out["timeout_journal"] = dict(uncaught=True, rows=len(list(Path(tmp).rglob("*.json"))))
            else:
                raise AssertionError("Expected timeout to escape")

    # Same exit status, different error classification. These are fake CompletedProcess results.
    fake_claude = subprocess.CompletedProcess([], 1, json.dumps({"result": "code", "is_error": False}), "failed")
    fake_codex = subprocess.CompletedProcess([], 1, "", "failed")
    with patch.object(R.subprocess, "run", return_value=fake_claude):
        c, _ = R.call_claude("unused", "low", "prompt", str(ROOT))
    with patch.object(R.subprocess, "run", return_value=fake_codex):
        x, _ = R.call_codex("unused", "low", "prompt", str(ROOT))
    assert not c["is_error"] and x["is_error"]
    out["nonzero_exit_classification"] = dict(claude_is_error=c["is_error"], codex_is_error=x["is_error"])
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
