"""Hetzner function lane; mocked HTTP only, with synthetic credentials."""
import io
import json
import urllib.error
import uuid
from email.message import Message
from http.client import IncompleteRead
from unittest.mock import MagicMock, patch
from urllib.request import build_opener
from urllib.response import addinfourl

import pytest

from bench import run as R


def sse(*chunks, done=True):
    data = b": keepalive\n\nevent: message\n" + b"".join(
        b"data: " + json.dumps(chunk).encode() + b"\n\n" for chunk in chunks)
    return io.BytesIO(data + (b"data: [DONE]\n\n" if done else b""))


def delta(content=None, **fields):
    return {"choices": [{"delta": {"content": content, **fields}}]}


def set_stream(call, *chunks, done=True):
    call.return_value.__enter__.return_value = sse(*chunks, done=done)


@pytest.fixture(autouse=True)
def api(monkeypatch, tmp_path):
    key = "test-" + uuid.uuid4().hex
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("HETZNER_INFERENCE_API_KEY", key)
    with patch.object(R.urllib.request, "build_opener") as opener:
        call = opener.return_value.open
        set_stream(call, delta("```python\n"), delta(reasoning_content="thinking", reasoning="more thinking"),
                   delta("def f(): pass\n```"), {"choices": [{"delta": {}, "finish_reason": "stop"}]}, {
            "choices": [],
            "usage": {"prompt_tokens": 30, "completion_tokens": 17,
                      "prompt_tokens_details": {"cached_tokens": 10},
                      "completion_tokens_details": {"reasoning_tokens": 9}},
        })
        yield call, key


def invoke():
    return R.call_hetzner("Qwen/Qwen3.6-35B-A3B-FP8", "default", "bench prompt", "/tmp")


def http_error(status, body):
    return urllib.error.HTTPError(R.HETZNER_BASE_URL + "/chat/completions", status,
                                  "request failed", {}, io.BytesIO(body.encode()))


def test_normal_and_request(api):
    call, key = api
    (row, raw) = invoke()
    assert not row["is_error"] and row["error"] is None
    assert row["text"] == "```python\ndef f(): pass\n```"
    assert (row["in_tok"], row["out_tok"], row["cached_tok"], row["reasoning_tok"]) == (30, 17, 10, 9)
    assert row["cache_write_tok"] == 0 and row["wall_s"] >= 0
    assert row["cost_usd"] == 0.0
    assert row["cost_kind"] == "free-tier (Hetzner experimental, no list price)"
    assert json.loads(raw)["usage"]["completion_tokens"] == 17
    message = json.loads(raw)["choices"][0]["message"]
    assert message["reasoning_content"] == "thinking" and message["reasoning"] == "more thinking"
    request = call.call_args.args[0]
    assert request.full_url == R.HETZNER_BASE_URL + "/chat/completions"
    assert request.method == "POST"
    assert request.get_header("Authorization") == "Bearer " + key
    assert request.get_header("Content-type") == "application/json"
    assert json.loads(request.data) == {"model": "Qwen/Qwen3.6-35B-A3B-FP8",
                                       "messages": [{"role": "user", "content": "bench prompt"}],
                                       "stream": True, "stream_options": {"include_usage": True}}
    assert call.call_args.kwargs == {"timeout": 120}


@pytest.mark.parametrize("content", ["", None])
def test_reasoning_only_keeps_completion_empty(api, content):
    call, _ = api
    set_stream(call, delta(content, reasoning_content="private reasoning"))
    row, raw = invoke()
    assert not row["is_error"] and row["text"] == ""
    assert row["in_tok"] == row["out_tok"] == row["cached_tok"] == row["reasoning_tok"] == 0
    assert json.loads(raw)["choices"][0]["message"]["content"] == ""
    assert json.loads(raw)["choices"][0]["message"]["reasoning_content"] == "private reasoning"


@pytest.mark.parametrize("parts", [("hel", "lo"), ('{ "x": ', ' 1 }'), ("", "")])
def test_usage_less_stream(api, parts):
    call, _ = api
    set_stream(call, *(delta(part) for part in parts), {"choices": [{"delta": {}, "finish_reason": "stop"}]})
    row, raw = invoke()
    assert not row["is_error"] and row["text"] == "".join(parts)
    assert json.loads(raw)["choices"][0]["message"]["content"] == row["text"]
    assert row["in_tok"] == row["out_tok"] == row["cached_tok"] == row["reasoning_tok"] == 0


def test_usage_comes_from_final_chunk(api):
    call, _ = api
    chunk = delta("hello")
    chunk["usage"] = {"prompt_tokens": 999, "completion_tokens": 999}
    set_stream(call, chunk, {"choices": [], "usage": {"prompt_tokens": 2, "completion_tokens": 3}})
    row, _ = invoke()
    assert not row["is_error"] and (row["in_tok"], row["out_tok"]) == (2, 3)


@pytest.mark.parametrize("status", [400, 401, 429, 500, 503, 504, 599])
def test_http_error_is_a_row(api, status):
    call, key = api
    call.side_effect = http_error(status, "echo: " + key)
    row, raw = invoke()
    assert row["is_error"] and row["text"] == ""
    assert f"HTTP {status}" in row["error"]
    assert row["error_type"] == "infrastructure"
    assert row["cost_usd"] == 0.0
    assert key not in json.dumps(row) + raw


@pytest.mark.parametrize("kind", ["network", "timeout", "truncated", "invalid-json", "invalid-response", "null-response"])
def test_failures_return_scrubbed_rows(api, kind):
    call, key = api
    if kind == "network": call.side_effect = urllib.error.URLError("connection: " + key)
    elif kind == "timeout": call.side_effect = TimeoutError("timeout: " + key)
    elif kind == "truncated": call.side_effect = IncompleteRead(key.encode())
    else:
        body = key if kind == "invalid-json" else "null" if kind == "null-response" else json.dumps({"choices": []})
        call.return_value.__enter__.return_value = io.BytesIO(b"data: " + body.encode() + b"\n\n")
    row, raw = invoke()
    assert row["is_error"] and row["error_type"] == "infrastructure"
    assert key not in json.dumps(row) + raw


@pytest.mark.parametrize("failure", ["eof", "incomplete", "timeout"])
def test_mid_stream_break_is_infrastructure(api, failure):
    call, key = api
    if failure == "eof":
        set_stream(call, delta("partial " + key), {"choices": [{"delta": {}, "finish_reason": "stop"}]}, done=False)
    else:
        # A socket failure after a valid chunk must discard the partial completion.
        response = MagicMock()
        response.readline.side_effect = [
            b"data: " + json.dumps(delta("partial " + key)).encode() + b"\n",
            IncompleteRead(key.encode()) if failure == "incomplete" else TimeoutError(key),
        ]
        call.return_value.__enter__.return_value = response
    row, raw = invoke()
    assert row["is_error"] and row["error_type"] == "infrastructure" and row["text"] == ""
    assert key not in json.dumps(row) + raw


def test_http_504_does_not_store_html(api):
    call, key = api
    error = http_error(504, "<html>" + key + "x" * 10000 + "</html>")
    error.msg = "gateway: " + key + "y" * 1000
    call.side_effect = error
    row, raw = invoke()
    assert row["is_error"] and row["error_type"] == "infrastructure"
    assert "HTTP 504" in row["error"] and len(row["error"]) <= 300
    assert key not in json.dumps(row) + raw and "<html>" not in row["error"] + raw


@pytest.mark.parametrize("late_line", [False, True])
def test_wall_cap_before_and_after_chunk(api, monkeypatch, late_line):
    call, _ = api
    response = MagicMock()
    call.return_value.__enter__.return_value = response
    clock = [0]
    monkeypatch.setattr(R.time, "monotonic", lambda: clock[0])
    def read():
        clock[0] = 1801
        return b"data: [DONE]\n"
    response.readline.side_effect = read
    with patch.object(R.threading, "Timer") as timer:
        if not late_line:
            timer.return_value.start.side_effect = lambda: clock.__setitem__(0, 1801)
        row, _ = invoke()
    assert row["is_error"] and row["error_type"] == "infrastructure"
    assert "1800s wall cap" in row["error"]
    assert timer.call_args.args[0] == 1800
    timer.return_value.cancel.assert_called_once()
    if not late_line: response.readline.assert_not_called()
    # The deadline interrupts the real socket rather than waiting on a read lock.
    timer.call_args.args[1]()
    response.fp.raw._sock.shutdown.assert_called_once_with(R.socket.SHUT_RDWR)


def test_key_split_across_chunks_is_redacted(api):
    call, key = api
    cut = len(key) // 2
    set_stream(call, delta(key[:cut], reasoning_content=key[:cut], reasoning=key[:cut]),
               delta(key[cut:], reasoning_content=key[cut:], reasoning=key[cut:]))
    row, raw = invoke()
    assert row["text"] == "[REDACTED]" and key not in json.dumps(row) + raw
    message = json.loads(raw)["choices"][0]["message"]
    assert message["reasoning_content"] == message["reasoning"] == "[REDACTED]"


def test_credentials_read_at_call_time_and_file_fallback(api, monkeypatch, tmp_path):
    call, key = api
    path = tmp_path / ".config" / "hetzner" / "inference.env"
    path.parent.mkdir(parents=True)
    path.write_text("# local config\nIGNORED=value\nexport HETZNER_INFERENCE_API_KEY='" + key + "' # comment\n")
    other = "test-" + uuid.uuid4().hex
    monkeypatch.setenv("HETZNER_INFERENCE_API_KEY", other)
    assert not invoke()[0]["is_error"]
    assert call.call_args.args[0].get_header("Authorization") == "Bearer " + other
    monkeypatch.delenv("HETZNER_INFERENCE_API_KEY")
    set_stream(call, delta("ok"))
    assert not invoke()[0]["is_error"]
    assert call.call_args.args[0].get_header("Authorization") == "Bearer " + key


def test_missing_credentials_do_not_call_network(api, monkeypatch):
    call, _ = api
    monkeypatch.delenv("HETZNER_INFERENCE_API_KEY")
    row, raw = invoke()
    assert row["is_error"] and "Missing Hetzner" in row["error"] and raw == ""
    call.assert_not_called()


def test_configs_and_cache_identity(api, monkeypatch):
    _, key = api
    assert R.CONFIGS["hetzner-qwen36"] == ("hetzner", "Qwen/Qwen3.6-35B-A3B-FP8", "default")
    assert R.CONFIGS["hetzner-qwen38"] == ("hetzner", "Qwen/Qwen3.8-27B", "default")
    with patch.object(R.subprocess, "run") as command, patch.object(R.hashlib, "sha256", wraps=R.hashlib.sha256) as digest:
        original = R.key_for("hetzner-qwen36", "p", 1, "prompt")
        identity = json.loads(digest.call_args.args[0])
        assert identity["flags"] == ["--base-url", R.HETZNER_BASE_URL, "--model", "Qwen/Qwen3.6-35B-A3B-FP8",
                                     "--stream", "--include-usage"]
        assert identity["cli_version"] == R.cli_version("hetzner")
        assert key not in json.dumps(identity)
        monkeypatch.setenv("HETZNER_INFERENCE_API_KEY", "test-" + uuid.uuid4().hex)
        assert R.key_for("hetzner-qwen36", "p", 1, "prompt") == original
        assert R.key_for("hetzner-qwen38", "p", 1, "prompt") != original
        monkeypatch.setattr(R, "HETZNER_BASE_URL", "https://example.invalid/api/v1")
        assert R.key_for("hetzner-qwen36", "p", 1, "prompt") != original
        command.assert_not_called()


@pytest.mark.parametrize("mode", ["success", "http", "network"])
def test_stored_rows_raw_and_logs_never_contain_key(api, monkeypatch, tmp_path, capsys, mode):
    call, key = api
    monkeypatch.setattr(R, "CALLS", str(tmp_path / "calls"))
    monkeypatch.setattr(R, "RAW", str(tmp_path / "raw"))
    monkeypatch.setattr(R, "prompt_for", lambda pid: "bench prompt")
    # Even a response that echoes an escaped credential must be safe to persist.
    escaped = "".join("\\u%04x" % ord(char) for char in key)
    body = '{"choices":[{"delta":{"content":"' + escaped + '"}}]}'
    if mode == "success":
        call.return_value.__enter__.return_value = io.BytesIO(b"data: " + body.encode() + b"\n\ndata: [DONE]\n\n")
    elif mode == "http": call.side_effect = http_error(429, body)
    else: call.side_effect = urllib.error.URLError("echo: " + key)
    status = R.one("hetzner-qwen36", "p", 1, "mock", 1)
    assert not status.startswith("stopped")
    stored = next((tmp_path / "calls").iterdir()).read_text()
    row = json.loads(stored)
    raw = next((tmp_path / "raw").iterdir()).read_text()
    captured = capsys.readouterr()
    assert key not in stored + raw + status + captured.out + captured.err
    assert escaped not in stored + raw
    assert row["text"] == ("[REDACTED]" if mode == "success" else "")
    if mode != "success":
        assert row["is_error"] and R.error_kind(row) == "infrastructure"
        call.side_effect = None
        set_stream(call, delta("ok"))
        R.one("hetzner-qwen36", "p", 1, "mock", 1)
        row = json.loads(next((tmp_path / "calls").iterdir()).read_text())
        assert not row["is_error"] and row["retry_count"] == 1
        assert row["previous_attempt"]["is_error"]
    assert R.one("hetzner-qwen36", "p", 1, "mock", 1) == "cached"


@pytest.mark.parametrize("status", [300, 301, 302, 303, 304, 305, 306, 307, 308, 399])
@pytest.mark.parametrize("location", [R.HETZNER_BASE_URL + "/redirected", "https://elsewhere.invalid/completions"])
def test_redirects_are_errors_without_a_second_request(api, status, location):
    headers = Message()
    headers["Location"] = location
    response = addinfourl(io.BytesIO(b"redirect body"), headers,
                          R.HETZNER_BASE_URL + "/chat/completions", status)
    response.msg = "redirect"
    transport = R.urllib.request.HTTPSHandler()
    transport.https_open = MagicMock(return_value=response)
    # Exercise urllib's real response/redirect dispatch with a mocked transport.
    with patch.object(R.urllib.request, "build_opener",
                      side_effect=lambda *handlers: build_opener(*handlers, transport)):
        row, raw = invoke()
    assert row["is_error"] and row["error_type"] == "infrastructure"
    assert f"HTTP {status}" in row["error"] and row["text"] == ""
    assert "redirect body" not in raw
    transport.https_open.assert_called_once()


@pytest.mark.parametrize("value, expected", [("42", 42), (17, 17), (None, None), ("invalid", None),
                                            ("3.5", None), ({}, None), ([], None), (float("inf"), None)])
def test_usage_tokens_are_int_or_none_in_rows_and_status(api, monkeypatch, tmp_path, value, expected):
    call, _ = api
    set_stream(call, delta("ok"), {"choices": [], "usage": {
        "prompt_tokens": value, "completion_tokens": value,
        "prompt_tokens_details": {"cached_tokens": value},
        "completion_tokens_details": {"reasoning_tokens": value},
    }})
    monkeypatch.setattr(R, "CALLS", str(tmp_path / "calls"))
    monkeypatch.setattr(R, "RAW", str(tmp_path / "raw"))
    monkeypatch.setattr(R, "prompt_for", lambda pid: "bench prompt")
    status = R.one("hetzner-qwen36", "p", 1, "mock", 1)
    row = json.loads(next((tmp_path / "calls").iterdir()).read_text())
    assert not row["is_error"]
    for field in ("in_tok", "out_tok", "cached_tok", "reasoning_tok", "cache_write_tok"):
        assert row[field] is None or type(row[field]) is int
        assert row[field] == (0 if field == "cache_write_tok" else expected)
    assert status.endswith(f"out={expected}")


def test_grader_child_environment_excludes_credentials(api, monkeypatch):
    from bench import grade_all as G
    names = ("HETZNER_INFERENCE_API_KEY", "OTHER_API_KEY", "GITHUB_TOKEN", "TOKEN", "SomeToken", "lower_api_key")
    for name in names: monkeypatch.setenv(name, "synthetic-secret")
    monkeypatch.setenv("BENCH_KEEP", "preserved")
    with patch.object(G.subprocess, "run") as child:
        child.return_value.stdout = '{"outcome": "pass"}'
        assert G.grade_text("p", "def f(): pass") == {"outcome": "pass"}
    env = child.call_args.kwargs["env"]
    assert all(name not in env for name in names)
    assert not any(name.upper().endswith(("_API_KEY", "TOKEN")) for name in env)
    assert env["BENCH_KEEP"] == "preserved"
    assert child.call_args.args[0][1:3] == ["-m", "bench.grade"]
    assert child.call_args.kwargs["cwd"] == R.ROOT
    assert all(R.os.environ[name] == "synthetic-secret" for name in names)


def test_scrubbed_grader_environment_reaches_sandbox(api, monkeypatch, tmp_path):
    from bench import grade_all as G
    # Use the real grader and sandbox; mock only the grader result so a small
    # synthetic candidate can report what the sandbox actually inherits.
    monkeypatch.setenv("OTHER_API_KEY", "synthetic-secret")
    monkeypatch.setenv("ACCESS_TOKEN", "synthetic-secret")
    monkeypatch.setenv("BENCH_KEEP", "preserved")
    real_run = G.subprocess.run
    observed = []
    def launch(cmd, **kwargs):
        probe = tmp_path / "probe.py"
        probe.write_text("import os\ndef probe():\n    return {'names': list(os.environ), 'kept': os.environ.get('BENCH_KEEP')}\n")
        driver = (
            "import json; from bench.grade import run_sandbox; "
            "print(json.dumps(run_sandbox(" + repr(str(probe)) + ", 'probe', [[]], 10)))"
        )
        result = real_run([cmd[0], "-c", driver], **kwargs)
        observed.append(json.loads(result.stdout))
        result.stdout = '{"outcome": "pass"}'
        return result
    with patch.object(G.subprocess, "run", side_effect=launch):
        G.grade_text("p", "def f(): pass")
    results, status = observed[0]
    assert status == "ok"
    env = results[0]["out"]
    assert env["kept"] == "preserved"
    assert not any(name.upper().endswith(("_API_KEY", "TOKEN")) for name in env["names"])
    # Also verify the unchanged grader's CLI works through the new call site.
    assert G.grade_text(R.problems.MAIN[0], "pass")["outcome"] == "no_code"
    for filename, expected in G.GRADER_SHA.items():
        with open(R.os.path.join(R.ROOT, "bench", filename), "rb") as source:
            assert R.hashlib.sha256(source.read()).hexdigest() == expected


@pytest.mark.parametrize("elapsed", [1790, 1800, 1801])
def test_wall_cap_applies_before_open(api, monkeypatch, elapsed):
    call, _ = api
    clock = [0]
    monkeypatch.setattr(R.time, "monotonic", lambda: clock[0])
    def key():
        clock[0] = elapsed
        return "synthetic-key"
    monkeypatch.setattr(R, "_hetzner_key", key)
    set_stream(call, delta("ok"))
    with patch.object(R.threading, "Timer"):
        row, _ = invoke()
    if elapsed < 1800:
        assert not row["is_error"]
        assert call.call_args.kwargs["timeout"] == 1800 - elapsed
    else:
        assert row["is_error"] and "1800s wall cap" in row["error"]
        call.assert_not_called()


def test_wall_cap_rechecked_after_connection(api, monkeypatch):
    call, _ = api
    clock = [0]
    monkeypatch.setattr(R.time, "monotonic", lambda: clock[0])
    response = MagicMock()
    def connect(*args, **kwargs):
        clock[0] = 1801
        return MagicMock(__enter__=MagicMock(return_value=response))
    call.side_effect = connect
    row, _ = invoke()
    assert row["is_error"] and "1800s wall cap" in row["error"]
    response.readline.assert_not_called()


def test_socket_timeout_tracks_remaining_wall_time(api, monkeypatch):
    call, _ = api
    clock = [0]
    monkeypatch.setattr(R.time, "monotonic", lambda: clock[0])
    response = MagicMock()
    call.return_value.__enter__.return_value = response
    def read():
        if clock[0] == 0:
            clock[0] = 1790
            return b"data: " + json.dumps(delta("ok")).encode() + b"\n"
        clock[0] = 1801
        return b"data: [DONE]\n"
    response.readline.side_effect = read
    with patch.object(R.threading, "Timer") as timer:
        row, _ = invoke()
    assert row["is_error"] and "1800s wall cap" in row["error"]
    assert [c.args[0] for c in response.fp.raw._sock.settimeout.call_args_list] == [120, 10]
    timer.return_value.cancel.assert_called_once()
