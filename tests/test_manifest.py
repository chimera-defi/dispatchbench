"""Published provenance must depend on run inputs, never on the current commit."""
import json
import subprocess

import pytest

from analysis import raw_runs, summarize


@pytest.fixture(scope="module")
def built():
    return summarize.build()


def test_manifest_is_independent_of_head(monkeypatch, built):
    summary, _, expected = built
    rows, agent = summarize.function_rows(), summarize.agentic_rows()
    manifests = []
    for sha in ("a" * 40, "b" * 40):
        monkeypatch.setattr(subprocess, "check_output", lambda *a, **kw: sha)
        manifests.append(summarize.manifest(rows, agent, summary))
    assert "git_sha" not in expected
    assert manifests[0] == manifests[1] == expected
    assert expected["generated_from"] and expected["cli_versions"]
    assert expected["models_ran"] and expected["exploratory"]


def test_published_manifest_and_raw_index_match_inputs(built):
    manifest = raw_runs.ROOT / "results/manifest.json"
    assert json.loads(manifest.read_text()) == built[2]
    assert raw_runs.OUTPUT.read_text() == raw_runs.render()

