#!/usr/bin/env bash
# Resume the Gemini (agy) cells that stopped on a 429: repeat 1 of p01-p12 for six agy configs and repeats 1-5 for gpt-oss-120b, then grade and tell google-orch-1125.
# Run by tools/agy-resume.timer. If the quota is still out, the exact error is posted and one more try is armed for 2 hours later.
set -u
cd "$(dirname "$0")/.."
OUT=results/2026-11-25-agy-function.jsonl
python3 -m bench.run --phase exploratory --configs hydrogen-low,hydrogen-medium,hydrogen-high,gemini38flash-low,agy-sonnet46-default,agy-opus46-default --problems all --repeats 1-1 --lanes 4 --retry-limits > cache/agy_resume.log 2>&1
python3 -m bench.run --phase exploratory --configs agy-gptoss120b-medium --problems all --repeats 1-5 --lanes 1 --retry-limits >> cache/agy_resume.log 2>&1
stopped=$(grep -c "stopped: quota" cache/agy_resume.log)
post() { python3 /home/agents/agent-host-chat-control/bin/coordination_bus_cli.py post --idempotency-key "dispatchbench-agy-resume-$(date +%Y%m%d%H%M)" --sender dispatchbench --recipient google-orch-1125 --kind report --summary "$1" >/dev/null 2>&1; }
if [ "$stopped" -gt 0 ]; then
  err=$(python3 -c "import json,glob;print(sorted((json.load(open(f)) for f in glob.glob('cache/calls/*.json') if 'RESOURCE_EXHAUSTED' in open(f).read()[:4000] and json.load(open(f)).get('cli')=='agy'),key=lambda d:d['ts'])[-1]['error'][:260])")
  post "DispatchBench agy resume: still quota-stopped. Last error: $err. Retrying in 2 hours."
  systemd-run --user --on-active=2h --unit=agy-resume-retry "$PWD/tools/agy_resume.sh" >/dev/null 2>&1
  exit 0
fi
python3 - <<'PY'
import json, os
from bench import grade_all
from bench.run import CALLS
es = [json.load(open(os.path.join(CALLS, f))) for f in os.listdir(CALLS) if f.endswith(".json")]
grade_all.main([e for e in es if e["cli"] == "agy" and not e["is_error"]], "results/2026-11-25-agy-function.jsonl")
PY
python3 -m analysis.agy_slice > /dev/null
post "DispatchBench agy resume finished: cells graded into $OUT; run make report and review before landing. See results/report/agy_slice.md on branch dbench/agy-lane."
