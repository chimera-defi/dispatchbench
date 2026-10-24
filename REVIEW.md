# Model-routing benchmark review

Reviewed base `d94fbc8` on branch `review-astra`, 2026-10-24. This is an advisory review of the benchmark, not an execution or routing approval. No benchmark model calls were made; Claude API spend for this review is **$0**. Existing benchmark results were not changed.

## Verdict on the fairness hypothesis

**The harness does restrict Claude-native orchestration, but the evidence does not show that this caused Claude to score worse.** The agentic track is not a clean comparison of native agents, and it cannot test same-family delegation. It reports 84/84 hidden-test passes, including 12/12 each for haiku-low, haiku-high and sonnet-medium. In the function track, haiku-high and sonnet-medium match sol61-high and Astra on the main ladder and L7. There is no observed Claude accuracy deficit here for an orchestration explanation to explain.

There are real asymmetries:

| Dimension | Evidence | Interpretation |
|---|---|---|
| Native tools and subagents | `bench/agentic/run.py:20-24` permits Claude only `Bash,Read,Edit,Write,Glob,Grep`; it does not equivalently pin Codex's feature/tool set. The 24 available Claude agentic init transcripts confirm exactly those six tools. | Claude cannot invoke its native Agent/Task tool. Codex's default feature surface is not a controlled match. Both retain shell access, so CLI delegation is not categorically prevented. No native orchestration advantage was measured. |
| Instructions/context | `bench/run.py:55-57`, `bench/agentic/run.py:21-24`; `PLAN.md:111-122` documents Codex global AGENTS injection and its behavioral effects. Fixtures contain ordinary task/package/test files, without equivalent task-specific CLAUDE.md/AGENTS.md guidance. | `--setting-sources ""` and `--ignore-user-config` are not proof of equivalent effective prompts. The Codex context contamination is observed; a clean Claude-native context ablation is absent. I did not inspect credentials or assume that disabling settings proves absence of all memory/instruction sources. |
| Successful delegation | Of 12 sol61-medium transcripts, **9 actual `kimi-delegate --task` invocations, all 9 authentication failures**. Example: `cache/agentic_raw/agentic-3cd04907cb996c697ff1d996fc2dee11ea220ecc8afab127c58441b12ecf49ef.out:18`. | This is failed third-family delegation, not successful Codex-family collaboration. Recorded `delegate_calls=23` includes discovery/cleanup commands matching a regex (`bench/agentic/run.py:25,78`), so it is not 23 completed reviews. It adds time/tokens to Codex; an accuracy benefit is unproved. |
| Tools-off functions | Common prompt at `bench/run.py:59-67`; Claude tools actually disabled, Codex instructed not to use tools with read-only sandbox. All **1,146** function rows contain **0 Codex tool items** in aggregate. | The enforcement asymmetry exists, but no recorded Codex tool-use advantage occurred in these rows. Tools-off function solving is a legitimate narrow experiment, not a native-agent benchmark. Raw function streams are not committed, so this is a parsed-telemetry finding. |
| Effort | Explicit model and effort passed at `bench/run.py:102,135`; the Claude high arm now exists. `bench/trim_probe.py:28-36` additionally strips Codex tools and base instructions for the separate bare arm. | “Low” is not an equal compute budget across families. Both families have high-effort evidence; bare Codex is a different harness and should remain a separate arm. There is no flag evidence here that Claude was accidentally forced to low in its high arm. |
| Limits/permissions | Functions: 1,200 seconds for both (`bench/run.py:103,136`). Agentic: 1,500 seconds for both (`bench/agentic/run.py:47,66`). Claude bypasses permissions; Codex has workspace-write sandbox (`:22-24`). | No unequal wall timeout was found. Permissions actually give Claude broader execution access. Child lifetime, failed calls and grading timeouts have separate bugs below. |
| Prices/cache | `analysis/summarize.py:31-44`; `results/prices.json`. | Observed Claude CLI dollars versus Codex list-price estimates is explicitly disclosed. They are not two measured invoices or an empirically measured quota exchange rate. Provider-cache exposure differs substantially; see finding 7. |

**Same-family delegation is untested.** The planner is hardcoded to Haiku and every builder to Codex (`bench/plan_first.py:21-23,57-66`). G compares a Haiku repair against one Luna same-model retry (`bench/gated_repair.py:21-28,104-113`), with only two triggered repairs in those matched high-Luna arms. Both finish 32/35. This is neither a Claude→Claude planner/builder arm nor a native parent/subagent experiment. The claim that Haiku “does the work” is compatible with these narrow results, but does not establish that delegation generally fails or that cross-family handoffs are optimal.

Recommended next design, **not run here**: keep a minimal single-agent track, and separately compare native orchestration with equivalent task instructions in CLAUDE.md/AGENTS.md, explicit same-family child models/effort, identical total dollar/time budgets including descendants, and a recorded effective tool/context manifest. For the handoff question, use Claude→Claude, Claude→Codex, Codex→Claude, Codex→Codex on the same fresh tasks and matched role budgets, with single-model controls. Do not spend a held-out set on selecting the matrix. First repair the accounting/replay problems below so the experiment can be interpreted.

## Findings ranked by potential effect on routing conclusions

### 1. High: the flagship→Haiku repair route has never exercised its repair branch

**Evidence:** `bench/gated_repair.py:27-28,135-145`; `analysis/luna_rescue.py:8`; `docs/readme.tmpl.md:11-19`. G runs the seven problems selected for Luna failures. Both sol61-high and Astra pass 35/35 with **zero repairs**. The headline 60/60 rows are standalone function solves, not 60 end-to-end pipeline trials. There are no flagship failed-build→Haiku repairs in this evidence.

**Effect:** The recommended *builder* has evidence. The proposed *fallback* and its effectiveness on flagship residual failures do not. A check on worked examples is also weaker than “a check fails” suggests: high-Luna+Haiku misses three genuinely failing builds without triggering repair; low-Luna+Haiku misses one. A policy can use this repair provision, but the benchmark has not validated it as reliability insurance. Same-family repair may be better or worse; two high-Luna repairs do not settle that.

**Show:** Run the offline command below; inspect `data.pipeline_G`: flagship repairs 0/35 each; high-Luna gated arms both 32/35 with 2 repairs and 3 untriggered failures. No new model calls required.

**Recommend:** Label the flagship rows “builder validated; fallback untested,” name the gate “statement examples,” and keep its 35-case evidence separate from the 60-case standalone result. Evaluate repairs on a separately collected failed-build set across both families, with coverage and regressions reported. Do not infer an optimal repair model from zero triggers.

The preference for sol61-high while Codex has quota is an **operator cost policy**, not demonstrated capability superiority: haiku-high also scores 60/60 and costs $0.002822/pass versus $0.018615 for sol61-high under the recorded accounting. The README does disclose both; the conditional billing objective should stay explicit.

### 2. High: native-agent results and clean-install cost/latency conclusions are confounded

**Evidence:** The tool/context/delegation rows above; `bench/agentic/run.py:20-25,64-81`; `docs/report.tmpl.md:33` calls Codex agentic numbers “upper bounds for a clean install.”

**Effect:** Claude's native subagent workflow was disabled, while Codex was affected by unrelated host instructions. The direction of an accuracy change from removing either restriction is unidentified. Even the “upper bound” claim is too strong: removing instructions can change planning, verification, errors and tool use, not merely subtract overhead. A clean run could take longer or solve fewer tasks. The current data support measured contaminated-run costs, not a counterfactual bound. No 100%-pass ceiling comparison establishes superiority on harder native repo work.

**Show:** `data.agentic` in the probe records tool sets, actual delegate invocation locations and failures. `sol61-medium` has 9 failed delegate calls; the available base Codex transcripts show no completed native collaboration events. Later flagship native-tool behavior cannot be checked from committed transcripts (finding 4).

**Recommend:** Publish effective input/tool manifests, scrubbed instruction hashes and all child receipts for future runs; remove the “upper bound” wording. Retain these as contaminated historical runs rather than silently relabeling them clean. Compare minimal and native tracks separately; do not just enable every connector for Claude and call that matched.

### 3. High: hidden-test-only success overlooks a real incomplete task and admits skipped-test false positives

**Evidence:** `bench/agentic/run.py:84-88,110-125` sets `ok` only from pytest exit status and records visible/hidden status separately; `analysis/summarize.py:107-115` uses only `hidden_pass` for the headline. Every TASK.md asks for all tests to pass. In `results/2026-10-22b-agentic.jsonl`, key `6f2f1a0dbd6c8ed873fc0f7f290678ecebe99a53f30959350f34e8a688e5aa15` is luna-low / t2 / repeat 2: visible **1 failed, 5 passed**, hidden **6 passed**. Its transcript at `cache/agentic_raw/agentic-6f2f1a0dbd6c8ed873fc0f7f290678ecebe99a53f30959350f34e8a688e5aa15.out:12` shows the agent's new test incorrectly expects two live entries after both older entries have expired.

**Effect:** Luna's package passes the hidden contract, but its delivered repo has failing tests and the requested task is incomplete. This is a bad added test, not evidence that the implementation is wrong. Full task completion is **11/12 Luna, 83/84 overall**, rather than every repo run being complete. The hidden-pass metric is disclosed, but interpreting it as complete coding-task success favors this Luna result.

**Probe:** With the unchanged, broken t2 starter, hidden tests give **5 failed, 1 passed**. The probe adds only a `conftest.py` skip hook and an empty requested regression file, then runs the actual `A.one` path with a fake model. It records **hidden_pass=true, visible_pass=true, own_tests=true, tests_tampered=[]**, despite **0 passed, 6 skipped** hidden tests. This is a demonstrated harness acceptance defect, **not an accusation that a recorded model used it**; the stored original rows all have positive expected hidden counts.

**Recommend:** Report both hidden functionality and complete-task success. Require visible+hidden passes, no invocation error, expected collected/passed test IDs and no unexpected skips/xfails. Run trusted grading outside candidate-controlled pytest configuration/hooks and verify the immutable original tests. File existence alone is insufficient evidence of regression coverage. Preserve candidate sources first, then regrade; do not overwrite old rows without a grading revision ID.

### 4. High: agentic outcomes cannot generally be replayed, particularly the flagship comparison

**Evidence:** `bench/agentic/run.py:114-128` retains a diff *stat*, deletes the entire working repo, and stores verdicts/raw stdout. It never saves a candidate tree or complete patch. `export()` at `:137-141` just republishes those verdicts. Of 84 rows, only **48** have `cache/agentic_raw` transcripts; **all 12 each for sol61-high, Astra and haiku-high are missing**. `docs/REPORT.md:217` nevertheless says all other result sets can be regraded. Codex file-change events do not always contain source (`analysis/agentic_tests.py:12-16`), so even the available transcripts are not a guaranteed source archive.

**Effect:** A reviewer cannot independently regrade the headline native repo results, verify their child activity, or apply a fixed grader to the actual delivered trees. Re-exporting cached verdicts is not regrading. This materially limits confidence in findings 2 and 3 without proving the original passes false.

**Show:** `data.agentic.*.transcripts` in the offline probe; inspect any `cache/agentic/<key>.json` for the absent patch/tree. No rerun is needed to identify the gap.

**Recommend:** Archive the final candidate tree/patch, trusted test digest, full structured grading output, effective flags/context and scrubbed stream before cleanup. Include grader/environment version in grading keys. Correct the reproducibility claim now; label unavailable historical artifacts rather than claiming to regenerate them.

### 5. Medium-high: Claude's spend guard is partial, bypassable, and misses billed failed calls

**Evidence:** `bench/run.py:92-98,152-156` counts only `cache/calls`. Agentic adds only its own cache (`bench/agentic/run.py:96-99,132-134`). Plan-first and repair call `call_claude` directly without any budget check (`bench/plan_first.py:43-60`, `bench/gated_repair.py:51-61,104-110`); trim does likewise (`bench/trim_probe.py:91-101`). The check does not reserve for calls already in flight. Claude commands have no `--max-budget-usd` (`bench/run.py:102`, `bench/agentic/run.py:46`).

**Show:** The mocked repair probe makes **one provider invocation with `CLAUDE_BUDGET_USD=0`**, caches its simulated $0.02, and `claude_spend()` still returns $0. Current committed cache costs are calls $1.61278838, agentic $0.84960569, trim $0.00249178, plan-first $0.06925582, gated repair $0.24822865. Thus **$0.31997625 of measured auxiliary cache spend** is absent from the README's $2.46 “Total spend.” The five cache directories total **$2.78237032**, excluding the pilot and unrecoverable ad hoc calls. Do not sum pipeline row totals to estimate spend: some calls are shared across arms.

**Effect:** The $8 guard is not a global experiment budget and could invalidate a tight spend-controlled comparison or exceed a review allowance. This is not evidence that the historical $10 ceiling was exceeded. Missing/null cost currently becomes $0 (`analysis/summarize.py:33-34`), hiding unknown charges.

**Recommend:** One append-only, unique-call ledger across all entry points, reserved concurrency budget and terminal receipts for errors/timeouts; propagate per-call Claude budget bounds. Treat unknown cost as unknown. Price all descendant calls, or prohibit delegation in the minimal track. Either include auxiliary spend or relabel the displayed total “function + agentic only” (`analysis/summarize.py:277-283`).

### 6. Medium: failure handling does not implement the pre-registered retry/stop rules

**Evidence:** `PLAN.md:56,102` promises one retry for harness errors and lane stop on quota/rate errors. `bench/run.py:149-150` returns “cached” for any prior error; `:167-172` only annotates quota errors; `:189-196` stops only on a budget-refused string. Timeouts at `:103,136` and agentic `:47,66` escape before a cache/spend entry is written. The subprocess timeout kills the direct process, not a deliberately managed process group, so descendant accounting/lifetime is also not controlled.

**Show:** Offline mocks: an initial transient error followed by the identical run produces **one call, then “cached”**; a two-attempt lane continues after a quota error (**two attempts**); a simulated timeout escapes with **no new ledger entry**. The script records these under `lifecycle`. All 1,146 existing function rows report no CLI error, so I do **not** claim this altered their recorded scores; unrecorded failed attempts cannot be audited from those rows.

**Recommend:** Structured attempt status and retry ordinal, exactly one permitted infrastructure retry, quota/rate lane stop, and cleanup/receipt writing in exception-safe paths. Keep infrastructure failures distinct from model mistakes. Record partial usage or explicit unknown cost before returning; no silent replacement of failures with successful retries.

### 7. Medium: cache state, timing and cost objectives are not paired enough to transfer economic rankings

**Evidence:** `analysis/summarize.py:31-44` uses observed cache discounts; `bench/run.py:189-196` runs configs in sequential lanes, not randomized paired task blocks. Added configs ran later; phase is absent from `key_for` (`:84-89`), intentionally allowing call reuse, so a new phase label is not a fresh trial. `bench/gated_repair.py:158` reports summed model wall time but omits the example gate's sandbox time (`:65-89,135`).

**Show:** Main-ladder cache token shares are **86.16% haiku-low, 14.69% haiku-high, 78.56% sol61-high, 79.68% Astra**. Repricing *the same Codex token traces* with zero cache hits raises sol61-high from **$0.018615 to $0.041573/pass**, Astra from **$0.075264 to $0.185126/pass**. These are sensitivity calculations, not forecasts of fresh runs. The probe does not reprice Claude because the benchmark does not retain a comparable Claude price schedule. The report already acknowledges cache sensitivity; the missing piece is applying a comparable scenario to both sides before claiming transferable price ratios.

**Effect:** Small cost differences can reverse with cache policy, and latency medians across different days/lanes are not controlled causal effects. A “free while quota remains” routing policy can still be reasonable, but token-list dollars do not measure quota consumption or opportunity cost. This limitation does not erase Haiku-high's large recorded cost advantage. Pipeline “fastest” means model-call wall time, not end-to-end validation latency.

**Recommend:** Preserve observed-cost tables; add common cold/warm workload scenarios for both providers, and measure quota rather than assuming list dollars track it. Randomize/interleave paired runs under a recorded concurrency/load schedule. Time gate+repair end to end. Cache reuse is fine for analyses, but record memberships separately and require fresh trial IDs for new measurements.

### 8. Medium-low: absent test-count data is rendered as exactly zero

**Evidence:** `analysis/report.py:326-330` filters the old `agentic_tests.json` for each config. For an absent config, `all([])` is true and `sum([])` is 0. The file has no rows for haiku-high, sol61-high or Astra; `docs/REPORT.md:125,128-129` therefore prints **0 test functions added** alongside 12/12 requested files. This is missing evidence, not zero tests. If `analysis.agentic_tests` is rerun, missing transcripts produce `None` lower bounds (`analysis/agentic_tests.py:133-135`), which the same `sum(...)` cannot handle.

**Effect:** The apparent testing-quality ranking is false for those three configs. It is not specifically anti-Claude: it misrepresents both added families. `make audit` does not regenerate or validate transcript coverage for this input (`analysis/audit.py:42-61`).

**Show:** Probe `data.agentic.*.test_count_rows` gives 0 for all three. Evaluate the expression on an empty list, or follow the missing-transcript branch and its `None` values.

**Recommend:** Render “unknown (0/12 transcripts available),” validate input coverage against the agentic manifest, and handle partial/null lower bounds explicitly. Do not fabricate 0 or ≥0 as a measured count.

### 9. Low now, material on rerun: agentic cache keys hash generated files and omit the grading procedure

**Evidence:** `bench/agentic/run.py:28-41` hashes every file under starter/hidden directories, including `__pycache__` and `.pytest_cache`; `:137-141` exports every cache row without a unique trial/harness filter. A changed grader alone does not invalidate `hidden_pass` because grading logic/environment is not keyed.

**Show:** The offline probe adds irrelevant generated bytecode to a temporary starter and confirms the tree digest changes. Merely testing/importing fixtures can create a second key for the same logical task/repeat. All old and new cached outcomes would then be exported and pooled by `analysis/summarize.py:100-109`.

**Recommend:** Hash a declared task-input manifest excluding generated artifacts, persist execution and grading revisions separately, and enforce unique `(experiment, harness, task, config, trial)` observations in analysis. I did not find a duplicate-row effect in the current 84-row agentic dataset; this is a reproducibility/rerun bug.

## Changes and verification

Added `bench/review_probe.py` and `results/review-astra/probe.json`; no production harness fixes or historical result rewrites. The script uses real repository data and real local pytest runs, with model entry points mocked for lifecycle/acceptance reproductions. Fixes above are recommendations, not silently applied changes to the experiment.

Reproduce all probe numbers:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m bench.review_probe --output results/review-astra/probe.json
```

The assertions pass. The skipped-test case deliberately demonstrates a defective pass; it is not an added benchmark completion. The only durable result artifact is under `results/review-astra/`. A Kimi independent-review attempt failed authentication before review; it supplied no evidence. No claim of an independent second-model review is made.

`PYTHONDONTWRITEBYTECODE=1 make audit` also passes: 16 generated files compared, 59 template literals checked against 38 allowed constants. This proves the existing rendering is consistent with its inputs, not that those inputs or acceptance criteria are sound. `git diff --check` passes; the full checker self-test was not rerun because no checker/problem implementation changed.

**Commit status: blocked by filesystem permissions, not completed.** `git add REVIEW.md bench/review_probe.py results/review-astra/probe.json` fails with `Unable to create '<repo>/.git/worktrees/mrb-astra/index.lock': Read-only file system`. This worktree is writable, but its external Git metadata is outside the sandbox's writable roots; approval escalation is unavailable. There is no review commit hash. Main, other worktrees, credentials, and existing result files were not modified. The three new files are ready for the orchestrator to stage and commit on `review-astra` with message `Review model-routing benchmark fairness and reproduce harness defects`.
