# Devin SWE-2.1: access, free-tier bench, real tasks (2026-11-25, exploratory)

PLAN.md deviation 28. **No SWE-2.1 number exists.** `devin auth status`: Tier Devin Free, Plan Free. These models each return exactly `Error: Upgrade to Pro to access this model (https://devin.ai/pricing)`: swe-2-1, swe-2-1-low, swe-2-1-medium, swe-2-1-high, swe-2-medium, swe-2-high, swe-2-max, swe-2-flash-high, swe-2-flash-max, adaptive and the alias `swe`. (swe-2-1-xhigh, -max and the Ultrafast variants were not probed; swe-2-1-low/-medium/-high were.) Result: the swe-2-1 rows are INCONCLUSIVE. Fault: the plan. Repair: a Pro month, the operator's call (bus msg-d8625b142a274328ae0c). Cognition's post (cognition.com/blog/swe-2-1, 2026-11-24) says SWE-2.1 is "Free through 12/8 on Desktop and CLI"; this login's CLI 3000.14.30821 still refuses it. Cause unknown (rollout, plan check, or Desktop only); not resolved.

Runs on Free: `swe-2-flash-medium` and `swe-1-6-slow`. The 12 x 5 exploratory run below is swe-2-flash-medium. **It is not SWE-2.1 and says nothing about it.**

## Function track, p01-p12 x 5, exploratory (rows: results/2026-11-25-devin-flash-function.jsonl)

| config | pass@1 | 95% CI | median s | p90 s | $/pass |
|---|---|---|---|---|---|
| devinflash-medium (swe-2-flash-medium, Free) | 80% (48/60) | 63%-93% | 16.4 | 222.7 | not reported (free tier) |
| devin16slow-default (swe-1-6-slow, 1 repeat) | 50% (6/12) | 25%-75% | 10.5 | 15.8 | not reported |
| terra61-low | 100% (60/60) | >=78% (all passed) | 10.3 | 20.9 | $0.010 |
| haiku-low | 95% (57/60) | 85%-100% | 10.0 | 16.0 | $0.0011 |
| sol61-medium | 97% (58/60) | 87%-100% | 22.6 | 36.2 | $0.014 |

Paired vs haiku-low: -15.0 pts (-33.3 to +0.0). By rung L1 10/10, L2 9/10, L3 8/10, L4 6/10, L5 7/10, L6 8/10. Per problem: p08_recur 1/5 (IndexError on a small case); p10 3/5; the rest 4-5/5. All 60 calls ran; no cap, quota or upgrade message appeared. Slow tail: p10-p12 took 170-360 s on several calls (p90 222.7 s), against about 20 s for the others. Not a test of the $20 plan.

## Three real tasks (disposable git worktrees; I read each diff and ran the check)

| task | via | result | time |
|---|---|---|---|
| 1. results/README.md: list 3 missing jsonl files | `devin-delegate`, as shipped | FAIL: edit rejected, no change | 18 s |
| 2. new pytest for `analysis.summarize.ci_text` | `devin-delegate`, as shipped | FAIL: file write rejected | 15 s |
| 3. crss README: add the `crss adopt` example | `devin-delegate`, as shipped | FAIL: edits rejected | 52 s |
| 1 again | `devin -p --permission-mode accept-edits` | PASS: 3 entries match the files' configs and phases; omits that followup-function also holds 20 sol61-high rows | 23 s |
| 2 again | `devin -p --permission-mode smart` | PASS: 3 tests, `pytest` 3 passed | 20 s |
| 3 again | `devin -p --permission-mode accept-edits` | PASS: correct line and alignment; copies the full usage sentence, so the line is long and says "such a transcript" with no antecedent | 200 s |

Fault in the first three: the wrapper passes `--permission-mode auto`, which in `-p` mode rejects edits ("warning: rejected a tool call that requires confirmation"). Repair: call `devin` with `accept-edits` (or `smart` when the task runs a command); the wrapper has no passthrough. Cost: not reported by the free tier (no tokens, no dollars). Which model ran is not named by the CLI for the default (no `--model`).

Raw outputs and diffs: results/devin/.
