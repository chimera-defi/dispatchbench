#!/usr/bin/env bash
# Resume the agy cells that stopped on a quota limit or an error: repeat 1 of p01-p12 for six configs and repeats 1-5 for gpt-oss-120b.
# Run by agy-resume.timer from the main checkout. Grades whatever completed, posts the outcome to google-orch-1125, and while cells
# are still limited re-arms itself 2 hours later (a fresh transient unit name each time).
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
cd "$(dirname "$0")/.."
LOG=cache/agy_resume.log
post() { python3 /home/agents/agent-host-chat-control/bin/coordination_bus_cli.py post --idempotency-key "dispatchbench-agy-resume-$(date +%Y%m%d%H%M%S)" --sender dispatchbench --recipient google-orch-1125 --kind report --summary "$1" >/dev/null 2>&1; }
command -v agy >/dev/null || { post "DispatchBench agy resume FAILED: agy not found on PATH ($PATH). Nothing was run."; exit 1; }
: > "$LOG"
python3 -m bench.run --phase exploratory --configs hydrogen-low,hydrogen-medium,hydrogen-high,gemini38flash-low,agy-sonnet46-default,agy-opus46-default --problems all --repeats 1-1 --lanes 4 --retry-limits >> "$LOG" 2>&1; rc1=$?
python3 -m bench.run --phase exploratory --configs agy-gptoss120b-medium --problems all --repeats 1-5 --lanes 1 --retry-limits >> "$LOG" 2>&1; rc2=$?
if [ "$rc1" -ne 0 ] || [ "$rc2" -ne 0 ]; then post "DispatchBench agy resume FAILED (bench.run exit $rc1/$rc2). Last log line: $(tail -n 1 "$LOG" | cut -c1-200)"; exit 1; fi
python3 - <<'PY'
import json, os
from bench import grade_all
from bench.run import CALLS
es = [json.load(open(os.path.join(CALLS, f))) for f in os.listdir(CALLS) if f.endswith(".json")]
grade_all.main([e for e in es if e["cli"] == "agy" and not e["is_error"]], "results/2026-11-25-agy-function.jsonl")
PY
python3 -m analysis.agy_slice > /dev/null
stopped=$(grep -c "stopped: quota" "$LOG"); errs=$(grep -c " ERR " "$LOG")
if [ "$stopped" -gt 0 ]; then
  err=$(grep -h -o "RESOURCE_EXHAUSTED[^\"]*" cache/calls/*.json 2>/dev/null | tail -n 1)
  post "DispatchBench agy resume: partly done, $stopped lane(s) still quota-stopped ($err). Completed cells are graded in the main checkout (uncommitted). Retrying in 2 hours."
  systemd-run --user --on-active=2h --unit="agy-resume-retry-$(date +%s)" "$PWD/tools/agy_resume.sh" >/dev/null 2>&1
  exit 0
fi
post "DispatchBench agy resume finished: $errs error cell(s) left; new rows graded into results/2026-11-25-agy-function.jsonl in the main checkout (uncommitted). Run make report, review, land."
