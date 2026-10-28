"""Regrade every stored t1_discount patch against the stricter hidden suite (grader_version 3). No model calls.

python3 -m bench.regrade_t1            # writes results/2026-10-28-t1-hidden-v2-regrade.jsonl

Each patch is applied to the starter repo and graded twice by the trusted runner: with the hidden suite as it was when the run
was graded (v1, from git history, to prove the replay reproduces the stored hidden_pass) and with the current v2 suite.
Rows without a stored patch (the 10-22 main run saved none) are listed with new_hidden_pass null."""
import glob, json, os, shutil, subprocess, tempfile

from bench.agentic import run as A

OUT = os.path.join(A.ROOT, "results", "2026-10-28-t1-hidden-v2-regrade.jsonl")
TASK = "t1_discount"
PATCH_DIRS = ("", "cache/agentic_patches", "cache/isolated/agentic_patches")


def patch_path(row):
    for c in ([row["patch"]] if row.get("patch") else []) + [os.path.join(d, row["key"] + ".patch") for d in PATCH_DIRS[1:]]:
        if os.path.exists(os.path.join(A.ROOT, c)): return os.path.join(A.ROOT, c)
    return None


def stored_rows():
    for f in sorted(glob.glob(os.path.join(A.ROOT, "results", "*agentic.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            if r.get("task") == TASK: yield os.path.relpath(f, A.ROOT), r


def grade(patch, hidden_file):
    t = os.path.join(A.TASKS, TASK)
    w = tempfile.mkdtemp(prefix="mrb-regrade-")
    try:
        shutil.copytree(os.path.join(t, "repo"), w, dirs_exist_ok=True)
        subprocess.run(["git", "-C", w, "init", "-q"], check=True)
        applied = subprocess.run(["git", "-C", w, "apply", "--binary", patch], capture_output=True, text=True)
        if applied.returncode: return None
        hid = A.hidden_pytest(w, os.path.join(t, "solution"), hidden_file)
        vis = A.visible_pytest(w)
        return bool(hid["ok"]), bool(vis["ok"])
    finally:
        shutil.rmtree(w, ignore_errors=True)


def v1_suite(tmp):
    """The suite as graded at run time: the current file without the v2 test (test_bool_pct_rejected and its comment)."""
    src = open(os.path.join(A.TASKS, TASK, "hidden", "test_hidden.py")).read()
    a = src.index("def test_bool_pct_rejected"); b = src.index("def test_codes")
    path = os.path.join(tmp, "test_hidden.py"); open(path, "w").write(src[:a] + src[b:]); return path


def main():
    new_hidden = os.path.join(A.TASKS, TASK, "hidden", "test_hidden.py")
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        old_suite = v1_suite(tmp)
        for f, r in stored_rows():
            p = patch_path(r)
            row = dict(key=r["key"], config=r["config"], file=f, repeat=r["repeat"], old_hidden_pass=bool(r["hidden_pass"]),
                       visible_pass=bool(r["visible_pass"]), patch=os.path.relpath(p, A.ROOT) if p else None)
            if p is None:
                row.update(new_hidden_pass=None, task_complete=None, replay_v1_hidden_pass=None, status="no patch stored")
            else:
                v1 = grade(p, old_suite); v2 = grade(p, new_hidden)
                if v1 is None or v2 is None:
                    row.update(new_hidden_pass=None, task_complete=None, replay_v1_hidden_pass=None, status="patch did not apply")
                else:
                    row.update(new_hidden_pass=v2[0], task_complete=v2[0] and v2[1], replay_v1_hidden_pass=v1[0], replay_visible_pass=v2[1],
                               status="regraded")
            out.append(row)
    out.sort(key=lambda r: (r["file"], r["config"], r["repeat"]))
    with open(OUT, "w") as fh:
        for r in out: fh.write(json.dumps(r, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    rows = main()
    flips = [r for r in rows if r["status"] == "regraded" and r["old_hidden_pass"] != r["new_hidden_pass"]]
    print(f"{len(rows)} t1 rows, {sum(r['status'] == 'regraded' for r in rows)} regraded, {len(flips)} flip: "
          + ", ".join(f"{r['config']} r{r['repeat']}" for r in flips))
