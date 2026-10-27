"""Agentic Grok invocation and cache/export contracts; no model calls."""
import json
import subprocess
from unittest.mock import patch

import pytest

from bench.agentic import run as A


def test_grok_repository_command_usage_and_cache_identity():
    raw = json.dumps(dict(text="done", num_turns=7, total_cost_usd=0.12,
                         usage=dict(input_tokens=100, cache_read_input_tokens=30,
                                    cache_creation_input_tokens=20, output_tokens=40, reasoning_tokens=10)))
    with patch.object(A, "grok_spend", return_value=0), patch.object(A.subprocess, "run", return_value=
            subprocess.CompletedProcess([], 0, raw, "")) as call:
        row, transcript = A.run_grok("grok-4.7", "high", "fix repo", "/task")
    assert transcript == raw and not row["is_error"]
    assert (row["in_tok"], row["cached_tok"], row["cache_write_tok"], row["out_tok"], row["reasoning_tok"]) == (150, 30, 20, 40, 10)
    assert row["turns"] == 7 and row["cost_usd"] == 0.12
    assert row["tool_calls"] is None  # JSON output does not expose individual calls.
    assert call.call_args.args[0] == [A.GROK, "-p", "fix repo", "-m", "grok-4.7",
                                     "--reasoning-effort", "high", "--cwd", "/task"] + A.GROK_FLAGS
    assert {"--always-approve", "--no-subagents", "--disable-web-search"} <= set(A.GROK_FLAGS)
    assert "--tools" not in A.GROK_FLAGS  # repository editing tools stay enabled
    assert call.call_args.kwargs == dict(stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd="/task", timeout=1500)
    with patch.object(A, "cli_version", return_value="test"):
        key = A.key_for("grok47-low", A.TASK_IDS[0], 1)
        with patch.object(A, "GROK_FLAGS", A.GROK_FLAGS + ["--max-turns", "1"]):
            assert A.key_for("grok47-low", A.TASK_IDS[0], 1) != key


@pytest.mark.parametrize("raw,code", [("invalid", 0), ("[]", 0), ('{"error":"overloaded"}', 1)])
def test_grok_repository_errors(raw, code):
    with patch.object(A, "grok_spend", return_value=0), patch.object(A.subprocess, "run", return_value=
            subprocess.CompletedProcess([], code, raw, "")):
        row, _ = A.run_grok("grok-4.7", "low", "fix", "/task")
    assert row["is_error"] and row["error_type"] == "infrastructure"


def test_grok_agentic_budget_and_scoped_export(tmp_path):
    with patch.object(A, "grok_spend", return_value=15), patch.object(A.subprocess, "run") as call:
        with pytest.raises(A.SpendLimit, match="Grok agentic spend"):
            A.run_grok("grok-4.7", "low", "fix", "/task")
        call.assert_not_called()
    for key, cfg in (("old", "haiku-low"), ("new", "grok47-low")):
        (tmp_path / (key + ".json")).write_text(json.dumps(dict(key=key, config=cfg,
            cli="grok" if key == "new" else "claude", task="t1", repeat=1)))
    out = tmp_path / "new.jsonl"
    with patch.object(A, "CACHE", str(tmp_path)):
        A.export(str(out), {"new"})
    assert [json.loads(line)["key"] for line in out.read_text().splitlines()] == ["new"]
    # A later `make grade` still exports historical lanes only.
    with patch.object(A, "CACHE", str(tmp_path)), patch.object(A, "OUT", str(out)):
        A.export()
    assert [json.loads(line)["key"] for line in out.read_text().splitlines()] == ["old"]
