"""Hetzner function lane; mocked HTTP only, with synthetic credentials."""
import io
import json
import urllib.error
import uuid
from http.client import IncompleteRead
from unittest.mock import patch

import pytest

from bench import run as R


@pytest.fixture(autouse=True)
def api(monkeypatch, tmp_path):
    key = "test-" + uuid.uuid4().hex
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("HETZNER_INFERENCE_API_KEY", key)
    with patch.object(R.urllib.request, "urlopen") as call:
        call.return_value.__enter__.return_value.read.return_value = json.dumps({
            "choices": [{"message": {"content": "```python\ndef f(): pass\n```"}}],
            "usage": {"prompt_tokens": 30, "completion_tokens": 17,
                      "prompt_tokens_details": {"cached_tokens": 10},
                      "completion_tokens_details": {"reasoning_tokens": 9}},
        }).encode()
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
    request = call.call_args.args[0]
    assert request.full_url == R.HETZNER_BASE_URL + "/chat/completions"
    assert request.method == "POST"
    assert request.get_header("Authorization") == "Bearer " + key
    assert request.get_header("Content-type") == "application/json"
    assert json.loads(request.data) == {"model": "Qwen/Qwen3.6-35B-A3B-FP8",
                                       "messages": [{"role": "user", "content": "bench prompt"}]}
    assert call.call_args.kwargs == {"timeout": 600}


@pytest.mark.parametrize("content", ["", None])
def test_reasoning_only_keeps_completion_empty(api, content):
    call, _ = api
    call.return_value.__enter__.return_value.read.return_value = json.dumps({
        "choices": [{"message": {"content": content, "reasoning_content": "private reasoning"}}],
    }).encode()
    row, raw = invoke()
    assert not row["is_error"] and row["text"] == ""
    assert row["in_tok"] == row["out_tok"] == row["cached_tok"] == row["reasoning_tok"] == 0
    assert json.loads(raw)["choices"][0]["message"]["content"] == content


@pytest.mark.parametrize("status", [400, 401, 429, 500, 503, 599])
def test_http_error_is_a_row(api, status):
    call, key = api
    call.side_effect = http_error(status, "echo: " + key)
    row, raw = invoke()
    assert row["is_error"] and row["text"] == ""
    assert f"HTTP {status}" in row["error"]
    assert row["error_type"] == ("infrastructure" if status == 429 or status >= 500 else "model")
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
        call.return_value.__enter__.return_value.read.return_value = body.encode()
    row, raw = invoke()
    assert row["is_error"] and row["error_type"] == "infrastructure"
    assert key not in json.dumps(row) + raw


def test_credentials_read_at_call_time_and_file_fallback(api, monkeypatch, tmp_path):
    call, key = api
    path = tmp_path / ".config" / "hetzner" / "inference.env"
    path.parent.mkdir(parents=True)
    path.write_text("# local config\nIGNORED=value\nexport HETZNER_INFERENCE_API_KEY='" + key + "' # comment\n")
    other = "test-" + uuid.uuid4().hex
    monkeypatch.setenv("HETZNER_INFERENCE_API_KEY", other)
    invoke()
    assert call.call_args.args[0].get_header("Authorization") == "Bearer " + other
    monkeypatch.delenv("HETZNER_INFERENCE_API_KEY")
    invoke()
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
        assert identity["flags"] == ["--base-url", R.HETZNER_BASE_URL, "--model", "Qwen/Qwen3.6-35B-A3B-FP8"]
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
    body = '{"choices":[{"message":{"content":"' + escaped + '"}}]}'
    if mode == "success": call.return_value.__enter__.return_value.read.return_value = body.encode()
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
        call.return_value.__enter__.return_value.read.return_value = b'{"choices":[{"message":{"content":"ok"}}]}'
        R.one("hetzner-qwen36", "p", 1, "mock", 1)
        row = json.loads(next((tmp_path / "calls").iterdir()).read_text())
        assert not row["is_error"] and row["retry_count"] == 1
        assert row["previous_attempt"]["is_error"]
    assert R.one("hetzner-qwen36", "p", 1, "mock", 1) == "cached"
