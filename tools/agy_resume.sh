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
# not before the quota reset (Wed 2 Dec 02:30 UTC): a run earlier than that only burns retries on the same 429
[ "$(date -u +%s)" -ge "$(date -u -d '2026-12-02 02:30' +%s)" ] || { post "DispatchBench agy resume skipped: started before the quota reset (2026-12-02 02:30 UTC). Nothing was run."; exit 0; }
TRIES=cache/agy_resume.tries; n=$(( $(cat "$TRIES" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$TRIES"
python3 -m bench.run --phase exploratory --configs hydrogen-low,hydrogen-medium,hydrogen-high,gemini38flash-low,agy-sonnet46-default,agy-opus46-default --problems all --repeats 1-1 --lanes 4 --retry-limits >> "$LOG" 2>&1; rc1=$?
python3 -m bench.run --phase exploratory --configs agy-gptoss120b-medium --problems all --repeats 1-5 --lanes 1 --retry-limits >> "$LOG" 2>&1; rc2=$?
if [ "$rc1" -ne 0 ] || [ "$rc2" -ne 0 ]; then post "DispatchBench agy resume FAILED (bench.run exit $rc1/$rc2). Last log line: $(tail -n 1 "$LOG" | cut -c1-200)"; exit 1; fi
python3 - <<'PY' >> "$LOG" 2>&1
import json, os
from bench import grade_all
from bench.run import CALLS
es = [json.load(open(os.path.join(CALLS, f))) for f in os.listdir(CALLS) if f.endswith(".json")]
grade_all.main([e for e in es if e["cli"] == "agy" and not e["is_error"]], "results/2026-11-25-agy-function.jsonl")
PY
rc3=$?
python3 -m analysis.agy_slice >> "$LOG" 2>&1; rc4=$?
if [ "$rc3" -ne 0 ] || [ "$rc4" -ne 0 ]; then post "DispatchBench agy resume: cells ran but grading failed (grade exit $rc3, agy_slice exit $rc4). Last log line: $(tail -n 1 "$LOG" | cut -c1-200)"; exit 1; fi
stopped=$(grep -c "stopped: quota" "$LOG"); errs=$(grep -c " ERR " "$LOG")
if [ "$stopped" -gt 0 ]; then
  err=$(grep -h -o "RESOURCE_EXHAUSTED[^\"]*" cache/calls/*.json 2>/dev/null | tail -n 1)
  if [ "$n" -ge 6 ]; then post "DispatchBench agy resume: still quota-stopped after $n runs ($err). Giving up; no more retries are armed."; exit 0; fi
  post "DispatchBench agy resume: partly done, $stopped lane(s) still quota-stopped ($err). Completed cells are graded in the main checkout (uncommitted). Retry $n of 6 in 2 hours."
  systemd-run --user --on-active=2h --unit="agy-resume-retry-$(date +%s)" "$PWD/tools/agy_resume.sh" >/dev/null 2>&1
  exit 0
fi
post "DispatchBench agy resume finished: $errs error cell(s) left; new rows graded into results/2026-11-25-agy-function.jsonl in the main checkout (uncommitted). Run make report, review, land."
