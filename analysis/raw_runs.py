"""Index published runs in place. Standard library only; no git or model calls."""
import argparse
from datetime import date
from fnmatch import fnmatchcase
import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/RAW_RUNS.md"
SUPPORTING = (
    "results/manifest.json", "results/prices.json", "results/agentic_tests.json",
    "results/quality.jsonl", "results/quality_meta.json",
)
CACHES = {
    "cache/calls": "Function completions, usage and call metadata",
    "cache/agentic": "Repo-task verdicts, usage and test summaries",
    "cache/grades": "Function verdicts and timing fractions",
    "cache/gated_repair": "Builds, visible-test gates and repair completions",
    "cache/plan_first": "Planner and builder completions",
    "cache/trim": "Harness-trim probe completions and usage",
    "results/solutions": "Graded Python answers and per-problem indexes",
}


def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def ignored(path, is_dir, patterns):
    """Match the root .gitignore's basename and slash-separated glob entries."""
    if "__pycache__" in path.parts:
        return True
    excluded = False
    for pattern in patterns:
        negate = pattern.startswith("!")
        pattern = pattern.removeprefix("!")
        directory_only = pattern.endswith("/")
        anchored = pattern.startswith("/") or "/" in pattern.rstrip("/")
        parts = pattern.strip("/").split("/")
        for length in range(1, len(path.parts) + 1):
            if directory_only and length == len(path.parts) and not is_dir:
                continue
            candidate = path.parts[:length]
            match = (len(parts) == len(candidate) and
                     all(fnmatchcase(value, glob) for value, glob in zip(candidate, parts))) if anchored else fnmatchcase(candidate[-1], pattern)
            if match:
                excluded = not negate
    return excluded


def published_files(directory, root=ROOT):
    """Walk actual files, including untracked files; prune ignored directories."""
    directory = Path(directory)
    if not directory.is_absolute():
        directory = root / directory
    patterns = [line.strip() for line in (root / ".gitignore").read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
    files = []
    for base, dirs, names in os.walk(directory):
        dirs[:] = sorted(name for name in dirs
                         if not ignored((Path(base) / name).relative_to(root), True, patterns))
        for name in names:
            path = Path(base) / name
            if path.is_file() and not ignored(path.relative_to(root), False, patterns):
                files.append(path)
    return sorted(files)


def directory_hash(directory, root=ROOT):
    directory = root / directory
    files = published_files(directory, root)
    lines = sorted(f"{sha256(path)}  {path.relative_to(directory).as_posix()}\n" for path in files)
    return len(files), hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def run_date(path, rows):
    match = re.search(r"\d{4}-\d{2}-\d{2}", path.name)
    if match:
        return match[0]
    dates = []
    for row in rows:
        for key, value in row.items():
            if key == "ts" or "date" in key.lower():
                match = re.match(r"\d{4}-\d{2}-\d{2}", str(value))
                if match:
                    try:
                        dates.append(date.fromisoformat(match[0]).isoformat())
                    except ValueError:
                        pass
    return min(dates, default="-")


def lanes(rows):
    families = set()
    for row in rows:
        if row.get("cli"):
            families.add(row["cli"].split("-")[0])
            continue
        # Pipelines and older appendix rows have no cli field.
        text = " ".join(str(row.get(key, "")) for key in ("config", "builder", "builder_kind"))
        for pattern, family in ((r"haiku|sonnet|claude", "claude"),
                                (r"luna|sol|astra|terra|codex|gpt-", "codex"),
                                (r"grok", "grok"), (r"devin|swe-", "devin")):
            if re.search(pattern, text):
                families.add(family)
    return ", ".join(sorted(families)) or "-"


def link(path):
    return f"[{path}](../{path})"


def render(root=ROOT):
    out = ["# Raw run index", "",
           "Each Run rows entry is one JSONL file. Each JSONL line is one recorded attempt or measurement.",
           "Files stay at their committed paths. Verify a file from the repo root with `sha256sum <path>`.",
           "For a folder, hash each included file. Use paths relative to that folder, without a leading `./`.",
           'The aggregate is SHA-256 over lexically sorted lines of `<sha256>  <relpath>\\n`, encoded as UTF-8.',
           "The walker skips root `.gitignore` entries and `__pycache__`; it includes untracked files.",
           "Run this one-line shell command from the repo root (change `d` for another folder):", "",
           "```bash",
           '''d=cache/calls; python3 -c 'from analysis.raw_runs import published_files, ROOT; import sys; d=ROOT/sys.argv[1]; print("\\n".join(p.relative_to(d).as_posix() for p in published_files(d)))' "$d" | (cd "$d" && while IFS= read -r f; do [ -z "$f" ] || sha256sum "$f"; done) | LC_ALL=C sort | sha256sum''',
           "```", "", "## Run rows", "",
           "Date uses the filename first, then the earliest recorded timestamp or date. Lanes name CLI families.", "",
           "| Run | Date | Lane(s) | Rows | SHA-256 | Link |",
           "|---|---|---|---:|---|---|"]
    paths = sorted(set((root / "results").glob("*.jsonl")) |
                   set((root / "results/appendix").rglob("*.jsonl")))
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        rows = [json.loads(line) for line in lines if line.strip()]
        out.append(f"| {path.stem} | {run_date(path, rows)} | {lanes(rows)} | {len(lines)} | `{sha256(path)}` | {link(path.relative_to(root).as_posix())} |")
    out += ["", "## Supporting files", "",
            "`manifest.json`, `summary.json` and `dataset.json` are regenerated by",
            "[analysis.summarize](../analysis/summarize.py) and [analysis.dataset](../analysis/dataset.py).",
            "Their hashes hold only for the commit you read. Regenerate this index after rebuilding them.", "",
            "| File | SHA-256 |", "|---|---|"]
    for path in SUPPORTING:
        out.append(f"| {link(path)} | `{sha256(root / path)}` |")
    out += ["", "## Raw call caches", "", "| Folder | Holds | Files | Aggregate SHA-256 |", "|---|---|---:|---|"]
    for path, description in CACHES.items():
        count, digest = directory_hash(path, root)
        out.append(f"| {link(path + '/')} | {description} | {count} | `{digest}` |")
    out += ["", "## Not published, and why", "",
            "- `cache/raw/` and `cache/codex_harness/raw/`: full CLI transcripts carry host context, instruction files and local paths. Never committed.",
            "- `cache/agentic_raw/`: dropped from history on 2026-10-26 for the same reason. Do not restore.",
            "- `cache/quality/`, `cache/expected/`, `cache/tmp/`, `cache/*.log` and `artifacts/`: scratch and logs, rebuilt by the runners.",
            "- `results/review-sol61/review.bundle`: a git bundle of two review commits. Its `REVIEW.md` copy names a local home path. It also needs a parent commit outside public history, so it cannot be imported. Flagged for removal. Read [the published review](../results/research/review-sol61/REVIEW.md) instead.",
            "", "## Pending", "",
            "Codex Terra (`gpt-6.1-terra`, `gpt-5.6-terra`) and Grok full-spectrum runs (branch `bench-runs`)",
            "and Devin `swe-1-6-slow` runs (branch `devin-runs`) are not on main yet.",
            "They will appear in the tables once landed and this file is regenerated.",
            "Pilot and trim Terra rows and the staged Grok rows above are separate from these pending runs.",
            "", "## Leak scan", "",
            "The publication scan covered home paths, email addresses, API keys and tokens",
            "(`sk-`, `sk-ant-`, `xai-`, `gh*_`, `AKIA`, JWTs and bearer tokens), private keys,",
            "IP addresses, the host name, instruction-file text and internal project words.",
            "Hits kept on purpose: the synthetic sandbox HOME for user `codex` set by",
            "[bench/codex_harness.py](../bench/codex_harness.py); `github.com/xai-org` (public vendor source link);",
            "Anthropic's noreply commit-trailer address in `.claude/workflows`; and",
            "`chimera-defi` / `chimera_defi` (repo owner). This doc describes the path and address without repeating them.", ""]
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if docs/RAW_RUNS.md differs")
    args = parser.parse_args(argv)
    fresh = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != fresh:
            print("raw_runs: docs/RAW_RUNS.md differs; run python3 -m analysis.raw_runs")
            return 1
        print("raw_runs: docs/RAW_RUNS.md is current")
    else:
        OUTPUT.write_text(fresh, encoding="utf-8")
        print("raw_runs: wrote docs/RAW_RUNS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
