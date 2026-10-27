"""Grok function-track contracts; no network or credentials."""
import json
import subprocess
from unittest.mock import patch

import pytest

from bench import run as R


def test_grok_json_usage_cost_and_command():
    payload = dict(text="```python\ndef f(): return 1\n```", num_turns=1,
                   total_cost_usd=0.0123, modelUsage={}, usage=dict(
                       input_tokens=120, cache_read_input_tokens=40,
                       output_tokens=50, reasoning_tokens=30))
    raw = json.dumps(payload)
    with patch.object(R, "check_grok_budget"), patch.object(R.subprocess, "run") as call:
        call.return_value = subprocess.CompletedProcess([], 0, raw, "")
        row, returned = R.call_grok("grok-4.7", "high", "problem", "/empty")
    assert returned == raw
    assert row["text"] == payload["text"]
    assert not row["is_error"] and row["error"] is None
    assert (row["in_tok"], row["cached_tok"], row["out_tok"], row["reasoning_tok"]) == (160, 40, 50, 30)
    assert row["cost_usd"] == 0.0123
    assert row["cost_kind"] == "measured (CLI total_cost_usd)"
    assert row["turns"] == 1 and row["wall_s"] >= 0
    cmd = call.call_args.args[0]
    assert cmd == [R.GROK, "-p", "problem", "-m", "grok-4.7", "--reasoning-effort", "high"] + R.GROK_FLAGS
    assert cmd[cmd.index("--tools") + 1] == "read_file"
    assert cmd[cmd.index("--disallowed-tools") + 1] == "read_file,search_tool,use_tool"
    assert call.call_args.kwargs["cwd"] == "/empty"
    assert "env" not in call.call_args.kwargs  # preserve HOME; never handle credentials


@pytest.mark.parametrize("stdout,code,stderr", [
    ("invalid", 0, ""), ("[]", 0, ""),
    (json.dumps(dict(error="overloaded", usage={})), 1, "connection failed"),
    (json.dumps(dict(is_error=True, text="model failure")), 0, ""),
])
def test_grok_errors(stdout, code, stderr):
    with patch.object(R, "check_grok_budget"), patch.object(R.subprocess, "run", return_value=
            subprocess.CompletedProcess([], code, stdout, stderr)):
        row, _ = R.call_grok("grok-4.7", "low", "problem", "/empty")
    assert row["is_error"] and row["error"]
    assert row["error_type"] == ("model" if code == 0 and 'model failure' in stdout else "infrastructure")


def test_grok_flags_in_key_and_version():
    with patch.object(R.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, "grok 1.0.70 (f50904eaee6c)\n", "")), patch.dict(R._versions, clear=True):
        assert R.cli_version("grok") == "1.0.70"
        key = R.key_for("grok47-low", "p01_overlap_minutes", 1, "prompt")
        with patch.object(R, "GROK_FLAGS", R.GROK_FLAGS + ["--disallowed-tools", "*"]):
            assert R.key_for("grok47-low", "p01_overlap_minutes", 1, "prompt") != key


def test_grok_budget_counts_retries_and_excludes_claude(tmp_path):
    (tmp_path / "grok.json").write_text(json.dumps(dict(cli="grok", cost_usd=24.0,
        cost_kind="measured (CLI total_cost_usd)", previous_attempt=dict(cli="grok", cost_usd=1.0))))
    (tmp_path / "claude.json").write_text(json.dumps(dict(cli="claude", cost_usd=0.5)))
    assert R.grok_spend(tmp_path) == 25.0
    assert R.claude_spend(tmp_path) == 0.5
    with patch.object(R, "grok_spend", return_value=60.0), patch.object(R.subprocess, "run") as call:
        with pytest.raises(R.SpendLimit, match="Grok spend"):
            R.call_grok("grok-4.7", "low", "problem", "/empty")
        call.assert_not_called()
