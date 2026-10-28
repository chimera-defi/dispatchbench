"""The t1_discount hidden-suite gap (luna-low isolated t1 r2 accepted a boolean percentage): pin the regrade and the new test."""
import json, os, shutil, tempfile
from pathlib import Path

from bench import regrade_t1
from bench.agentic import run as A


def rows():
    return [json.loads(l) for l in Path(regrade_t1.OUT).read_text().splitlines()]


def test_flip_set_is_pinned():
    done = [r for r in rows() if r["status"] == "regraded"]
    flips = sorted((r["config"], r["repeat"], r["file"]) for r in done if r["old_hidden_pass"] != r["new_hidden_pass"])
    assert flips == [("luna-low", 2, "results/2026-10-25-isolated-agentic.jsonl")]
    assert all(r["old_hidden_pass"] and not r["new_hidden_pass"] for r in done if (r["config"], r["repeat"]) == ("luna-low", 2))
    assert len(done) == 16 and all(r["replay_v1_hidden_pass"] == r["old_hidden_pass"] for r in done)  # the replay reproduces every stored grade
    assert [r["status"] for r in rows() if r["status"] != "regraded"] == ["no patch stored"] * 21
    assert all(r["task_complete"] == (r["new_hidden_pass"] and r["replay_visible_pass"]) for r in done)


def test_regrade_matches_the_stored_rows_and_patches_exist():
    stored = {r["key"]: (f, r) for f, r in regrade_t1.stored_rows()}
    assert {r["key"] for r in rows()} == set(stored) and len(stored) == 37
    for r in rows():
        f, s = stored[r["key"]]
        assert (r["file"], r["config"], r["old_hidden_pass"]) == (f, s["config"], bool(s["hidden_pass"]))
        if r["status"] == "regraded": assert os.path.exists(os.path.join(A.ROOT, r["patch"]))


def test_reference_passes_v2_and_bool_is_rejected():
    t = os.path.join(A.TASKS, "t1_discount")
    hid = A.hidden_pytest(os.path.join(t, "solution"), os.path.join(t, "solution"), os.path.join(t, "hidden", "test_hidden.py"))
    assert hid["ok"] and "test_hidden.py::test_bool_pct_rejected" in hid["collected_ids"]
    assert A.grader_version("t1_discount") == 3
