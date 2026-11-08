"""Constants and the row export that report-side code still imports from the retired one-off appendix runners.

Runner code (trim_probe, plan_first, gated_repair) was removed in the 2026-11 shrink; see git tag pre-shrink.
  trim levels: cumulative Codex config knobs (bench.run.codex_flags uses them for the luna-low-bare cache key)
  PLANNER, BUILDERS, CONFIGS: model and effort of appendix arms F and G (summarize.py prints them)
python3 -m bench.arms export-trim    # cache/trim/*.json -> results/2026-10-22b-trim.jsonl (make grade)"""
import json, os, sys

from bench.run import CODEX_FLAGS, write_rows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(ROOT, "bench", "pilot")
CACHE = os.path.join(ROOT, "cache", "trim")
OUT = os.path.join(ROOT, "results", "2026-10-22b-trim.jsonl")
MIN_INST = os.path.join(PILOT, "min_instructions.txt")
# The cache key holds the placeholder <MIN_INST>, not the file, so a changed file must not silently reuse cached calls.
MIN_INST_SHA = "47eee3a1a40de1c1ea690e4ebb6abf00241430c3fba42e5a01b9deebdab26df3"

TOOL_FEATURES = ["multi_agent", "apps", "browser_use", "browser_use_external", "computer_use", "image_generation", "memories", "plugins",
                 "goals", "view_image", "tool_suggest", "sleep_tool", "skill_search", "in_app_browser", "hooks", "remote_plugin",
                 "skill_mcp_dependency_install", "workspace_dependencies", "worktrees"]
LEVELS = {"base": []}
LEVELS["nodoc"] = LEVELS["base"] + ["-c", "project_doc_max_bytes=0"]
LEVELS["noctx"] = LEVELS["nodoc"] + ["-c", "include_environment_context=false", "-c", "include_permissions_instructions=false"]
LEVELS["nofeat"] = LEVELS["noctx"] + [x for f in TOOL_FEATURES for x in ("--disable", f)] + ["-c", 'web_search="disabled"']
LEVELS["mininst"] = LEVELS["nofeat"] + ["-c", "model_instructions_file=<MIN_INST>"]
LEVELS["noshell"] = LEVELS["mininst"] + [x for f in ("shell_tool", "unified_exec", "unified_exec_tty", "shell_snapshot") for x in ("--disable", f)]


def flags(level):
    return CODEX_FLAGS + [x.replace("<MIN_INST>", json.dumps(MIN_INST)) for x in LEVELS[level]]


PLANNER = ("claude-haiku-5-5", "low")
BUILDERS = {"haiku-low-plan+luna-low": ("gpt-6-luna", "low"), "haiku-low-plan+luna-high-bare": ("gpt-6-luna", "high")}
CONFIGS = {
    "luna-high-bare+haiku-on-fail": ("gpt-6-luna", "high"),
    "luna-high-bare+retry-on-fail": ("gpt-6-luna", "high"),
    "luna-low+haiku-on-fail": ("gpt-6-luna", "low"),
    "luna-high-bare+haiku-review-all": ("gpt-6-luna", "high"),
    "luna-low+haiku-review-all": ("gpt-6-luna", "low"),
    "astra-medium+haiku-on-fail": ("gpt-6-astra", "medium"),
    "sol61-high+haiku-on-fail": ("gpt-6.1-sol", "high"),
}


def export():
    rows = [json.load(open(os.path.join(CACHE, f))) for f in sorted(os.listdir(CACHE)) if f.endswith(".json")] if os.path.isdir(CACHE) else []
    rows.sort(key=lambda r: (r["step"], r["config"], r["problem"], r["round"]))
    write_rows(OUT, [json.dumps({k: v for k, v in r.items() if k != "text"}, sort_keys=True) + "\n" for r in rows])
    print(f"{len(rows)} trim rows -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    if sys.argv[1:] != ["export-trim"]:
        raise SystemExit(__doc__)
    export()
