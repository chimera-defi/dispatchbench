"""Publication freshness, links and accidental host-context leakage."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

import pytest

from analysis import raw_runs

ROOT = Path(__file__).resolve().parents[1]
DOCS = (ROOT / "docs/RAW_RUNS.md", ROOT / "docs/SETUP.md")


def test_raw_run_index_is_current():
    assert raw_runs.render() == DOCS[0].read_text(encoding="utf-8")


@pytest.mark.parametrize("path", DOCS, ids=lambda path: path.name)
def test_doc_links_exist(path):
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8"))
    assert links, f"{path.name} has no links"
    for target in links:
        parsed = urlsplit(target)
        assert not parsed.scheme and not parsed.netloc, f"expected a local path: {target}"
        assert (path.parent / unquote(parsed.path)).exists(), f"{path.name}: {target}"


@pytest.mark.parametrize("path", DOCS, ids=lambda path: path.name)
def test_docs_do_not_leak_host_context(path):
    text = path.read_text(encoding="utf-8")
    assert "/home/" not in text
    assert "/Users/" not in text
    assert not re.search(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9.-]*[A-Z0-9])?\.[A-Z]{2,}", text, re.I)
    for pattern in os.environ.get("DISPATCHBENCH_PRIVATE_PATTERNS", "").split(","):
        if pattern.strip():
            assert not re.search(pattern.strip(), text, re.I)


@pytest.mark.parametrize("private_patterns", [None, "", r"private[-_]machine, internal\.example"])
def test_doc_leak_patterns_are_optional(tmp_path, monkeypatch, private_patterns):
    path = tmp_path / "doc.md"
    path.write_text("Generic setup instructions.\n")
    if private_patterns is None:
        monkeypatch.delenv("DISPATCHBENCH_PRIVATE_PATTERNS", raising=False)
    else:
        monkeypatch.setenv("DISPATCHBENCH_PRIVATE_PATTERNS", private_patterns)
    test_docs_do_not_leak_host_context(path)
    if private_patterns:
        for text in ("PRIVATE-machine", "internal.example"):
            path.write_text(text)
            with pytest.raises(AssertionError):
                test_docs_do_not_leak_host_context(path)


def test_folder_digest_skips_ignored_files_and_sorts_hash_lines(tmp_path):
    (tmp_path / ".gitignore").write_text("cache/raw/\ncache/tmp/\ncache/*.log\n*.pyc\n")
    included = {"cache/calls/z.json": b"z", "cache/calls/nested/a.json": b"a"}
    excluded = ("cache/raw/transcript", "cache/tmp/scratch", "cache/debug.log",
                "cache/calls/__pycache__/x", "cache/calls/module.pyc")
    for name, content in {**included, **dict.fromkeys(excluded, b"ignored")}.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    lines = sorted(f"{hashlib.sha256(content).hexdigest()}  {name.removeprefix('cache/')}\n"
                   for name, content in included.items())
    assert raw_runs.directory_hash("cache", tmp_path) == (
        2, hashlib.sha256("".join(lines).encode()).hexdigest())


def test_check_rejects_stale_output_without_writing(tmp_path, monkeypatch):
    output = tmp_path / "RAW_RUNS.md"
    output.write_text("stale\n")
    monkeypatch.setattr(raw_runs, "OUTPUT", output)
    monkeypatch.setattr(raw_runs, "render", lambda: "fresh\n")
    assert raw_runs.main(["--check"]) == 1
    assert output.read_text() == "stale\n"
    assert raw_runs.main([]) == 0
    assert raw_runs.main(["--check"]) == 0


def test_dates_and_families_from_older_row_schemas():
    rows = [{"ts": "2026-10-24T00:00:00Z", "config": "haiku-low-plan+luna-low"},
            {"date": "2026-10-23", "config": "grok47-high"},
            {"date": "invalid", "builder": "gpt-6.1-sol"}]
    assert raw_runs.run_date(Path("2026-10-22b-function.jsonl"), rows) == "2026-10-22"
    assert raw_runs.run_date(Path("rescue.jsonl"), rows) == "2026-10-23"
    assert raw_runs.run_date(Path("rescue.jsonl"), []) == "-"
    assert raw_runs.lanes(rows) == "claude, codex, grok"


def test_run_index_handles_invalid_rows_and_recursive_paths(tmp_path, monkeypatch):
    results = tmp_path / "results"
    nested = results / "nested/deeper"
    nested.mkdir(parents=True)
    (results / "rescue.jsonl").write_text("\n  \nmalformed\nnull\n")
    (nested / "rescue.jsonl").write_text(
        '\n{"ts": "2026-10-24T00:00:00Z", "cli": "codex"}\n'
        '\t\ninvalid JSON\nnull\n[]\n42\n"string"\n'
        '{"date": "2026-10-23", "cli": "claude"}\n')
    monkeypatch.setattr(raw_runs, "SUPPORTING", ())
    monkeypatch.setattr(raw_runs, "CACHES", {})
    rendered = raw_runs.render(tmp_path)
    assert "| rescue | - | - | 2 |" in rendered
    assert "| nested/deeper/rescue | 2026-10-23 | claude, codex | 7 |" in rendered
    assert "`Rows` = non-empty lines" in rendered
    assert "`-` means no timestamp recorded" in rendered


def test_published_folder_command_reproduces_digest():
    text = DOCS[0].read_text()
    command = text.split("```bash\n", 1)[1].split("\n```", 1)[0]
    result = subprocess.run(["bash", "-o", "pipefail", "-c", command], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    assert result.stdout.split()[0] == raw_runs.directory_hash("cache/calls")[1]
