"""Hetzner function lane; mocked HTTP only, with synthetic credentials."""
import io
import json
import urllib.error
import uuid
from http.client import IncompleteRead
from unittest.mock import MagicMock, patch

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
    with patch.object(R.urllib.request, "urlopen") as call:
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
