import json, shutil, subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from bench import run as R
from bench.agentic import run as A


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(R, "cli_version", lambda cli: "offline")
    monkeypatch.setattr(A, "cli_version", lambda cli: "offline")
    monkeypatch.setattr(R, "CLAUDE", "/model-calls-forbidden")
    monkeypatch.setattr(R, "CODEX", "/model-calls-forbidden")
    monkeypatch.setattr(A, "CLAUDE", "/model-calls-forbidden")
    monkeypatch.setattr(A, "CODEX", "/model-calls-forbidden")


@pytest.fixture
def task(tmp_path, monkeypatch):
    tasks = tmp_path / "tasks"; t = tasks / "t1"; repo = t / "repo"
    (repo / "tests").mkdir(parents=True); (t / "hidden").mkdir()
    (repo / "thing.py").write_text("VALUE = False\n")
    (repo / "tests/test_visible.py").write_text("def test_visible(): assert True\n")
    (t / "hidden/test_hidden.py").write_text("from thing import VALUE\ndef test_hidden(): assert VALUE\n")
    shutil.copytree(repo, t / "solution")
    (t / "TASK.md").write_text("Fix thing. Add tests/test_new.py.\n")
    for name, value in {"TASKS": tasks, "CACHE": tmp_path / "agentic", "RAW": tmp_path / "raw", "PATCHES": tmp_path / "patches"}.items():
        monkeypatch.setattr(A, name, str(value), raising=False)
    return t


def fake_agent(edit):
    def call(mid, eff, prompt, w):
        edit(Path(w))
        return dict(is_error=False, error=None, in_tok=0, cached_tok=0, out_tok=0, cost_usd=None), ""
    return call


def agent_row():
    return json.loads(next(Path(A.CACHE).glob("*.json")).read_text())


def test_candidate_pytest_hooks_and_config_cannot_skip_hidden(task, monkeypatch):
    def edit(w):
        (w / "tests/conftest.py").write_text("import pytest\ndef pytest_collection_modifyitems(items):\n for item in items: item.add_marker(pytest.mark.skip(reason='bypass'))\n")
        (w / "pytest.ini").write_text("[pytest]\naddopts = -k nonexistent\n")
        (w / "tests/test_new.py").write_text("")
    monkeypatch.setattr(A, "run_codex", fake_agent(edit))
    A.one("luna-low", "t1", 1, 1)
    row = agent_row()
    assert row["hidden_pass"] is False
    assert row["hidden"]["passed"] == 0
    assert row["hidden"]["failed"] == 1
    assert row["task_complete"] is False


def test_visible_failure_prevents_task_completion(task, monkeypatch):
    def edit(w):
        (w / "thing.py").write_text("VALUE = True\n")
        (w / "tests/test_new.py").write_text("def test_new(): assert False\n")
    monkeypatch.setattr(A, "run_codex", fake_agent(edit))
    A.one("luna-low", "t1", 1, 1)
    row = agent_row()
    assert row["hidden_pass"] is True
    assert row["visible_pass"] is False
    assert row["task_complete"] is False


@pytest.mark.parametrize("marker", ["skip(reason='skip')", "xfail(reason='xfail')", "xfail(reason='xpass')"])
def test_hidden_skip_and_xfail_are_not_passes(task, marker):
    h = task / "hidden/test_hidden.py"
    h.write_text("import pytest\n@pytest.mark." + marker + "\ndef test_hidden(): assert " + ("True" if "xpass" in marker else "False") + "\n")
    result = A.hidden_pytest(str(task / "repo"), str(task / "repo"), str(h))
    assert result["ok"] is False
    assert result["expected_ids"] == ["test_hidden.py::test_hidden"]


def test_candidate_cannot_remove_expected_hidden_ids(task):
    (task / "hidden/test_hidden.py").write_text("from thing import VALUE\nif VALUE:\n def test_hidden(): assert True\n")
    (task / "repo/thing.py").write_text("VALUE = True\n")
    candidate = task.parent / "candidate"; candidate.mkdir()
    (candidate / "thing.py").write_text("VALUE = False\n")
    result = A.hidden_pytest(str(candidate), str(task / "repo"), str(task / "hidden/test_hidden.py"))
    assert result["ok"] is False
    assert result["expected_ids"] == ["test_hidden.py::test_hidden"]
    assert result["collected_ids"] == []


@pytest.fixture
def function_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "CALLS", str(tmp_path / "calls"))
    monkeypatch.setattr(R, "RAW", str(tmp_path / "raw"))
    monkeypatch.setattr(R, "key_for", lambda *a: "key")
    monkeypatch.setattr(R, "prompt_for", lambda pid: "prompt")
    return tmp_path / "calls/key.json"


def test_function_timeout_is_persisted(function_cache, monkeypatch):
    monkeypatch.setattr(R, "call_codex", Mock(side_effect=subprocess.TimeoutExpired("mock", 1)))
    R.one("luna-low", "p1", 1, "test", 1)
    row = json.loads(function_cache.read_text())
    assert row["outcome"] == "timeout" and row["is_error"]
    assert row["cost_usd"] is None


def test_agentic_timeout_is_persisted(task, monkeypatch):
    monkeypatch.setattr(A, "run_codex", Mock(side_effect=subprocess.TimeoutExpired("mock", 1)))
    A.one("luna-low", "t1", 1, 1)
    row = agent_row()
    assert row["outcome"] == "timeout" and row["is_error"]
    assert row["cost_usd"] is None and row["task_complete"] is False


@pytest.mark.parametrize("track", ["function", "agentic"])
def test_cached_infrastructure_error_gets_one_retry(track, function_cache, task, monkeypatch):
    module = R if track == "function" else A
    fp = function_cache if track == "function" else Path(A.CACHE) / (A.key_for("luna-low", "t1", 1) + ".json")
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(dict(is_error=True, error="temporary infrastructure failure", error_type="infrastructure", cost_usd=None)))
    call = Mock(side_effect=subprocess.TimeoutExpired("mock", 1))
    monkeypatch.setattr(module, "call_codex" if track == "function" else "run_codex", call)
    invoke = (lambda: R.one("luna-low", "p1", 1, "test", 1)) if track == "function" else (lambda: A.one("luna-low", "t1", 1, 1))
    invoke(); invoke()
    assert call.call_count == 1
    row = json.loads(fp.read_text())
    assert row["retry_count"] == 1 and row["previous_attempt"]["is_error"]


@pytest.mark.parametrize("track", ["function", "agentic"])
@pytest.mark.parametrize("error", ["quota exhausted", "rate limit exceeded"])
def test_quota_or_rate_limit_stops_lane(track, error, monkeypatch):
    module = R if track == "function" else A
    monkeypatch.setattr(module, "one", Mock(return_value="stopped: " + error))
    args = ["run", "--configs", "luna-low", "--repeats", "1-3", "--lanes", "1"]
    args += ["--phase", "test", "--problems", "p1,p2"] if track == "function" else ["--tasks", "t1,t2"]
    monkeypatch.setattr("sys.argv", args)
    monkeypatch.setattr(R, "claude_spend", lambda: 0)
    if track == "agentic": monkeypatch.setattr(A, "export", lambda: None)
    module.main()
    assert module.one.call_count == 1


@pytest.mark.parametrize("track", ["function", "agentic"])
def test_claude_nonzero_returncode_is_error(track, monkeypatch):
    module = R if track == "function" else A
    payload = {"type": "result", "result": "code", "total_cost_usd": 0.01}
    monkeypatch.setattr(R, "claude_spend", lambda: 0)
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess(a, 1, json.dumps(payload), "rate limit exceeded"))
    call = R.call_claude if track == "function" else A.run_claude
    row, _ = call("claude", "low", "prompt", "/tmp")
    assert row["is_error"] is True
    assert "rate limit" in row["error"]


@pytest.mark.parametrize("track", ["function", "agentic"])
@pytest.mark.parametrize("error", ["quota exhausted", "rate_limit_error"])
def test_error_row_signals_stop_and_is_never_retried(track, error, function_cache, task, monkeypatch):
    module = R if track == "function" else A
    result = dict(is_error=True, error=error, wall_s=0, cost_usd=None)
    call = Mock(return_value=(result, ""))
    monkeypatch.setattr(module, "call_codex" if track == "function" else "run_codex", call)
    invoke = (lambda: R.one("luna-low", "p1", 1, "test", 1)) if track == "function" else (lambda: A.one("luna-low", "t1", 1, 1))
    assert invoke().startswith("stopped")
    assert invoke().startswith("stopped")
    assert call.call_count == 1


@pytest.mark.parametrize("track", ["function", "agentic"])
def test_cached_model_error_is_not_retried(track, function_cache, task, monkeypatch):
    module = R if track == "function" else A
    fp = function_cache if track == "function" else Path(A.CACHE) / (A.key_for("luna-low", "t1", 1) + ".json")
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(dict(is_error=True, error="model declined", error_type="model")))
    call = Mock(side_effect=AssertionError("model errors must not retry"))
    monkeypatch.setattr(module, "call_codex" if track == "function" else "run_codex", call)
    status = R.one("luna-low", "p1", 1, "test", 1) if track == "function" else A.one("luna-low", "t1", 1, 1)
    assert status == "cached"


def test_success_requires_all_visible_and_hidden_tests(task, monkeypatch):
    def edit(w):
        (w / "thing.py").write_text("VALUE = True\n")
        (w / "tests/test_new.py").write_text("def test_new(): assert True\n")
    monkeypatch.setattr(A, "run_codex", fake_agent(edit))
    A.one("luna-low", "t1", 1, 1)
    row = agent_row()
    assert row["visible_pass"] and row["hidden_pass"] and row["task_complete"]
    assert row["hidden"]["expected_ids"] == row["hidden"]["collected_ids"]


def test_grader_version_changes_new_cache_key(task, monkeypatch):
    key = A.key_for("luna-low", "t1", 1)
    monkeypatch.setattr(A, "GRADER_VERSION", A.GRADER_VERSION + 1)
    assert A.key_for("luna-low", "t1", 1) != key
