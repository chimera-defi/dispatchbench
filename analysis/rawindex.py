"""Loader for the raw-run index: the only place besides analysis.summarize that reads results/*.jsonl for the file list.
analysis.dataset folds file_index() into dataset.json's generated_from; analysis.raw_runs renders it. Standard library only."""
from datetime import date
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SUPPORTING = (
    "results/manifest.json", "results/prices.json", "results/agentic_tests.json",
    "results/quality.jsonl", "results/quality_meta.json",
)
def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


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


REPO_TASK_FILES = ("2026-10-22b-agentic", "2026-10-25-isolated-agentic", "2026-10-27-grok-agentic")


def repo_task_counts(root):
    """Per config and file: runs that passed our hidden tests, and runs that are task complete (hidden and visible tests pass)."""
    out = []
    for name in REPO_TASK_FILES:
        path = root / "results" / f"{name}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for config in sorted({r["config"] for r in rows}):
            rr = [r for r in rows if r["config"] == config]
            hidden = sum(bool(r["hidden_pass"]) for r in rr)
            done = sum(bool(r.get("task_complete", r["visible_pass"] and r["hidden_pass"])) for r in rr)
            out.append(f"| {name} | {config} | {hidden}/{len(rr)} | {done}/{len(rr)} |")
    return out



def file_index(root=ROOT):
    """One entry per results/**/*.jsonl: run id, path, rows (non-empty lines), date, lanes, sha256."""
    out = []
    paths = sorted((root / "results").rglob("*.jsonl"))
    for path in paths:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = []
        for line in lines:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
        run = path.relative_to(root / "results").with_suffix("").as_posix()
        out.append({"run": run, "path": path.relative_to(root).as_posix(), "rows": len(lines), "date": run_date(path, rows), "lanes": lanes(rows), "sha256": sha256(path)})
    return out


def supporting(root=ROOT):
    return [(path, sha256(root / path)) for path in SUPPORTING]
