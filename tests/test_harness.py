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


def test_codex_calls_use_clean_home(tmp_path, monkeypatch):
    host = tmp_path / "host"; host.mkdir()
    codex = host / ".codex"; codex.mkdir()
    (codex / "AGENTS.md").write_text("Host instructions must not load")
    monkeypatch.setenv("HOME", str(host))
    monkeypatch.setenv("CODEX_HOME", str(codex))
    homes = []

    def run(cmd, **kwargs):
        env = kwargs.get("env", {})
        assert "CODEX_HOME" in env
        clean = Path(env["CODEX_HOME"])
        assert clean != codex and clean.is_dir()
        assert not (clean / "AGENTS.md").exists()
        assert {p.name for p in clean.iterdir()} == {"auth.json"}
        assert (clean / "auth.json").is_symlink()
        assert (clean / "auth.json").readlink() == codex / "auth.json"
        assert Path(env["HOME"]) != host
        assert "--ignore-user-config" in cmd
        homes.append(clean)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    for call in (R.call_codex, A.run_codex):
        call("test-model", "low", "offline prompt", str(tmp_path))
    assert len(homes) == 2 and homes[0] != homes[1]
    assert all(not p.exists() for p in homes)


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
    if track == "agentic": monkeypatch.setattr(A, "export", lambda *args, **kwargs: None)
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


def legacy_entry(config, task):
    import hashlib
    cli, mid, eff = A.CONFIGS[config]
    blob = dict(track="agentic", config=config, model=mid, effort=eff, cli=cli, cli_version="offline",
                flags=A.CLAUDE_FLAGS if cli == "claude" else A.CODEX_FLAGS, prompt=(task / "TASK.md").read_text(),
                task="t1", task_tree=A.tree_hash(str(task / "repo"), str(task / "hidden")), repeat=1)
    key = hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()
    row = dict(key=key, config=config, task="t1", repeat=1, hidden_pass=True, visible_pass=True, is_error=False)
    path = Path(A.CACHE) / (key + ".json"); path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(row))
    return path


@pytest.mark.parametrize("config", ["luna-low", "haiku-low"])
def test_legacy_cache_reuse_respects_codex_isolation(task, monkeypatch, config):
    legacy = legacy_entry(config, task); before = legacy.read_bytes()
    current = Path(A.CACHE) / (A.key_for(config, "t1", 1) + ".json")
    assert not current.exists()
    forbidden = Mock(side_effect=AssertionError("legacy verdict must prevent model calls"))
    codex = Mock(side_effect=subprocess.TimeoutExpired("offline", 1))
    monkeypatch.setattr(A, "run_claude", forbidden); monkeypatch.setattr(A, "run_codex", codex)
    status = A.one(config, "t1", 1, 1)
    assert not forbidden.called
    assert legacy.read_bytes() == before
    if config == "luna-low":
        assert codex.call_count == 1
        assert json.loads(current.read_text())["outcome"] == "timeout"
    else:
        assert status == "cached (grader_version=1)"
        assert not codex.called and not current.exists()


def test_regrade_explicitly_bypasses_legacy_cache(task, monkeypatch):
    legacy = legacy_entry("haiku-low", task); before = legacy.read_bytes()
    call = Mock(side_effect=subprocess.TimeoutExpired("mock", 1))
    monkeypatch.setattr(A, "run_claude", call)
    A.one("haiku-low", "t1", 1, 1, regrade=True)
    assert call.call_count == 1 and legacy.read_bytes() == before
    current = json.loads((Path(A.CACHE) / (A.key_for("haiku-low", "t1", 1) + ".json")).read_text())
    assert current["grader_version"] == A.GRADER_VERSION and current["outcome"] == "timeout"


def test_export_selects_newest_grader_for_each_trial(task, tmp_path, monkeypatch):
    cache = Path(A.CACHE); cache.mkdir()
    old = dict(config="luna-low", task="t1", repeat=1, ts="2099-01-01", hidden_pass=True)
    new = dict(old, grader_version=2, ts="2026-01-01", hidden_pass=False)
    latest = dict(new, ts="2026-02-01", hidden_pass=True)
    other_repeat = dict(old, repeat=2)
    other_task = dict(old, task="t2")
    other_config = dict(old, config="haiku-low")
    sources = [old, new, latest, other_repeat, other_task, other_config]
    for i, row in enumerate(sources): (cache / f"{i}.json").write_text(json.dumps(row))
    (cache / "inflight.json.tmp").write_text("incomplete JSON")
    before = {p: p.read_bytes() for p in cache.iterdir()}
    output = tmp_path / "export.jsonl"; monkeypatch.setattr(A, "OUT", str(output))
    A.export()
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(rows) == 4
    selected = {(r["config"], r["task"], r["repeat"]): r for r in rows}
    assert len(selected) == 4 and selected[("luna-low", "t1", 1)] == latest
    assert set(selected) == {("luna-low", "t1", 1), ("luna-low", "t1", 2), ("luna-low", "t2", 1), ("haiku-low", "t1", 1)}
    assert before == {p: p.read_bytes() for p in cache.iterdir()}


def test_regrade_flag_is_forwarded_to_trials(monkeypatch):
    monkeypatch.setattr(A, "one", Mock(return_value="cached"))
    monkeypatch.setattr(A, "export", lambda *args, **kwargs: None)
    monkeypatch.setattr("sys.argv", ["run", "--configs", "luna-low", "--tasks", "t1", "--repeats", "1", "--lanes", "1", "--regrade"])
    A.main()
    A.one.assert_called_once_with("luna-low", "t1", 1, 1, regrade=True)
