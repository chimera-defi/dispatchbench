"""Rerun the host-instruction ablation without changing historical caches/results.

python3 -m bench.isolated --dry-run
python3 -m bench.isolated --track main
python3 -m bench.isolated --track hard
python3 -m bench.isolated --track agentic

Function tracks retain the main/hard problem sets and repeats 1-5. The four
Codex configs already evaluated on agentic tasks retain repeats 1-3. All four
current tasks imply 48 agentic runs; select three with --agentic-tasks for 36.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shlex
import sys
import tempfile

from bench import grade, grade_all, problems, run
from bench.agentic import run as agentic
from bench.codex_env import isolated_codex_env

AGENTIC_CONFIGS = ("luna-low", "sol61-medium", "sol61-high", "astra-medium")


def preview(config, track):
    _, model, effort = run.CONFIGS[config]
    flags = agentic.CODEX_FLAGS if track == "agentic" else run.codex_flags(config)
    with tempfile.TemporaryDirectory(prefix="mrb-preview-work-") as work:
        with isolated_codex_env() as env:
            cmd = [run.CODEX, "exec", "-m", model, "-c", f"model_reasoning_effort={effort}"] + flags + ["-C", work, "<task prompt>"]
            print("Sample argv (prompt abbreviated): " + shlex.join(cmd))
            print("Env keys: " + ",".join(sorted(env)))
            print(f"HOME={env['HOME']} CODEX_HOME={env['CODEX_HOME']} (only auth.json symlink)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--track", choices=("all", "main", "hard", "agentic"), default="all")
    ap.add_argument("--dry-run", action="store_true", help="print plan and sample argv/env; no CLI or API calls")
    ap.add_argument("--lanes", type=int, choices=range(1, 5), default=4)
    ap.add_argument("--reps", type=int, default=0, help="stage 1: run only the first N tries (0 = all); reruns stop early unless stage 1 differs")
    ap.add_argument("--agentic-tasks", default="all", help="all, or comma-separated task IDs")
    a = ap.parse_args()
    tasks = agentic.TASK_IDS if a.agentic_tasks == "all" else a.agentic_tasks.split(",")
    if not tasks or len(tasks) != len(set(tasks)) or any(t not in agentic.TASK_IDS for t in tasks):
        ap.error("--agentic-tasks must contain distinct known task IDs")
    tracks = ("main", "hard", "agentic") if a.track == "all" else (a.track,)
    root = Path(run.ROOT)
    cache = root / "cache" / "isolated"
    run.CALLS = str(cache / "calls")
    run.RAW = agentic.RAW = str(cache / "raw")
    agentic.CACHE = str(cache / "agentic")
    agentic.PATCHES = str(cache / "agentic_patches")
    grade_all.GRADES = str(cache / "grades")
    grade.EXPECTED_DIR = str(cache / "expected")

    for track in tracks:
        if track == "agentic":
            configs, items, repeats = AGENTIC_CONFIGS, tasks, range(1, 4)
        else:
            configs = ("luna-low" if track == "main" else "sol61-high",)
            items = problems.MAIN if track == "main" else problems.HARD
            repeats = range(1, 6)
        if a.reps: repeats = range(1, min(a.reps, len(repeats)) + 1)
        output = root / "results" / f"2026-10-25-isolated-{track}.jsonl"
        count = len(configs) * len(items) * len(repeats)
        print(f"[isolated/{track}] {count} calls: {','.join(configs)}; {len(items)} tasks/problems; repeats 1-{max(repeats)}", flush=True)
        print(f"Results: {output.relative_to(root)}; cache: {cache.relative_to(root)}", flush=True)
        if a.dry_run:
            for config in configs:
                preview(config, track)
            continue

        def lane(config):
            for rep in repeats:
                for item in items:
                    if track == "agentic":
                        msg = agentic.one(config, item, rep, a.lanes, regrade=True)
                    else:
                        msg = run.one(config, item, rep, "isolated", a.lanes)
                    print(f"[isolated/{track}] {config} {item} r{rep}: {msg}", flush=True)
                    if msg.startswith(("refused", "stopped")): return

        with ThreadPoolExecutor(a.lanes) as ex:
            list(ex.map(lane, configs))
        output.parent.mkdir(exist_ok=True)
        if track == "agentic":
            keys = {agentic.key_for(c, t, r) for c in configs for t in items for r in repeats}
            agentic.export(output=str(output), keys=keys)
        else:
            keys = [run.key_for(c, p, r, run.prompt_for(p)) for c in configs for p in items for r in repeats]
            entries = [json.loads((Path(run.CALLS) / f"{k}.json").read_text()) for k in keys if (Path(run.CALLS) / f"{k}.json").exists()]
            grade_all.main(entries=entries, output=str(output))

    if a.dry_run:
        argv = [sys.executable, "-m", "bench.isolated"] + [x for x in sys.argv[1:] if x != "--dry-run"]
        print("Run: " + shlex.join(argv))


if __name__ == "__main__":
    main()
