# Review: model-routing-bench fairness and routing validity

Reviewed 2026-10-24, against `d94fbc8` on `review-sol61`. This is advisory evidence for the operator/orchestrator. No model calls, Claude spend, credential access, main changes, pushes, or changes to existing benchmark results were made.

## Verdict on the fairness hypothesis

**Partly supported at the harness level; not established as a cause of worse Claude scores.** Claude's native subagent tool is excluded in the repo track. Codex retains its stock tool surface and receives host instructions that alter its workflow. This is not a comparison of each family's best native agent. However, **all 84 repo runs passed**, including all Claude runs, so there is no observed Claude agentic accuracy deficit to explain. On the main function ladder, Haiku-low beats Luna-low (57/60 versus 46/60), and Sonnet-medium beats sol61-medium (60/60 versus 58/60). Haiku-high, Sonnet-medium, sol61-high and Astra-medium reach the tested ceiling. None of these observations establishes their ordering on larger native workflows.

The stronger hypothesis, **a family delegates better to its own family**, remains unanswered. Haiku planning for Luna and Haiku reviewing Codex are measured, with one narrow Luna retry comparator; a balanced planner/worker or builder/repairer family matrix is absent. Failed attempts to invoke Kimi from Codex are not evidence of successful delegation, much less same-family delegation.

**Counterevidence to a blanket Codex-favoured interpretation:**

- The function user prompt is identical across families (`bench/run.py:59-67`, `79-81`); grading uses the same problem, reference and fixed seed (`bench/grade.py:48-51`, `73-101`). All **823 recorded Codex function calls have zero tool items**. Available tools therefore did not produce recorded tool-assisted function solutions. This does not remove differences in system prompts or instruction overhead.
- Repo prompts and starting files are shared and hashed (`bench/agentic/run.py:37-42`, `100-108`). Hidden tests arrive after generation (`115-117`). Model-call timeouts are equal within each track: 1200 seconds for functions (`bench/run.py:103`, `136`) and 1500 for repos (`bench/agentic/run.py:47`, `66`). No evidence of a family-specific timeout limit was found.
- Claude's repo permission mode bypasses permission checks, while Codex has a workspace-write sandbox (`bench/agentic/run.py:21-24`). That difference gives Claude broader filesystem execution permissions; it does not uniformly favour Codex.
- Both families receive explicit model and effort flags (`bench/run.py:102`, `135`; `bench/agentic/run.py:46`, `65`). The fast tier is an explicit separate Codex configuration (`bench/run.py:38-50`), not a hidden default-tier advantage. The flagship comparisons and Haiku-high are appropriately labelled exploratory.
- The paired bootstrap does pair problems (`analysis/stats.py:25-37`). Luna-high's combined escalation/exploratory ladder still contains exactly five attempts per problem, not an overweighted subset (`analysis/summarize.py:250-252`). I found no confirmed family-specific scoring rule or statistical aggregation bug there.

## Reproduction and evidence

From the repository root:

```bash
python3 results/review-sol61/probe.py > /tmp/model-routing-review.json
python3 -m analysis.audit
```

The first command makes **zero model calls**. It reads committed evidence, runs two tiny pytest fixtures in temporary directories, and mocks CLI invocations for failure-path probes. Its captured output is `results/review-sol61/probe.json`. Pytest timing text can vary on rerun. The audit passed: 16 generated files compared, 59 template literals checked against 38 allowed constants; captured in `results/review-sol61/audit.txt`. Audit success establishes rendering consistency with the input rows, not that the input rows or their interpretation are sound.

The findings below are ordered by likely effect on routing conclusions. Confirmed defects, unsupported generalizations, and unobserved failure risks are distinguished explicitly.

## Findings

### 1. High: the repo comparison does not measure native family strengths, and Codex's host context changes the workload

**Evidence:** `bench/agentic/run.py:21-24` restricts Claude to `Bash,Read,Edit,Write,Glob,Grep`, excluding the native subagent tool. All 24 available Claude init transcripts confirm exactly those six tools; they also advertise agents, skills and built-in plugins. Example: `cache/agentic_raw/agentic-2c4b9788bf7e6a9a53ee2217eaa6b492802a69a79922c2a3b967574846fc6c27.out:1`. A listed agent is not a usable Agent tool. `--strict-mcp-config` removes configured MCP access. Codex's flags disable skill instructions, but do not similarly enumerate or disable its entire native tool/delegation surface.

The host `AGENTS.md` effect is documented in `PLAN.md:114`, `121`, `124` and independently recoverable. The probe reproduces **57/97 sol61-medium shell commands matching the host-context pattern**. Those are command-text matches, not a measured percentage of wasted time: some commands combine setup with useful task work. More decisively, it finds **nine actual `kimi-delegate --task` invocations, all exit 126**. Example failure: `cache/agentic_raw/agentic-3cd04907cb996c697ff1d996fc2dee11ea220ecc8afab127c58441b12ecf49ef.out:18`.

`--setting-sources ""` should not be treated as proof that all Claude context was disabled: the installed 2.1.308 `claude --help` describes it as selecting settings sources, whereas `--bare` separately mentions disabling CLAUDE.md discovery. The retained init inventory confirms that advertised customizations remain. **I did not establish that a host CLAUDE.md was actually injected**, nor that the advertised skills were callable with this tool whitelist.

**Effect:** these numbers describe constrained CLI workflows on this host, not intrinsic native-agent capability. The observed Codex detours plausibly increase its cost/time, so the direction is not simply anti-Claude. The report's claim that Codex repo costs/times are clean-install "upper bounds" (`docs/REPORT.md:45`) is not a measured counterfactual: changing instructions can change the whole solution path.

**Show it:** probe keys `claude_recorded_toolsets` and `sol61_medium_delegation`; inspect the two cited transcript lines; run `claude --help` without a model call.

**Recommended fix:** name this a shell/file-tool track. For a separate native-agent track, retain each family's native worker tools, give identical task context in the appropriate instruction format, and record the effective tools/context plus successful child identities and usage. Compare with a genuinely isolated restricted track. Do not change the current dataset's label into proof of native parity or disadvantage.

### 2. High: the flagship-to-Haiku repair rule has zero measured repair exposure; same-family superiority cannot be inferred

**Evidence:** `bench/gated_repair.py:21-28` supplies Codex builders, Haiku repair/review, and one Luna retry arm. `bench/plan_first.py:21-23` supplies only a Haiku planner and Luna builders. There is no Claude-builder/Claude-repairer versus Claude-builder/Codex-repairer comparison, no sol61 same-family repair control, and no native subagent experiment.

The probe reproduces:

| Pipeline | Runs | Repair invocations | Final passes |
|---|---:|---:|---:|
| sol61-high → Haiku on example failure | 35 | **0** | 35 |
| Astra-medium → Haiku on example failure | 35 | **0** | 35 |
| Luna-high bare → Haiku on failure | 35 | 2 | 32 |
| Luna-high bare → Luna retry on failure | 35 | 2 | 32 |
| Luna-low → Haiku on failure | 35 | 13 | 34 |

The two Luna-high repair arms share builds (`bench/gated_repair.py:118-127`), which is a good control, but **two repair triggers** cannot rank families. Also the gate checks statement examples only (`65-89`), not an arbitrary failed repository check. The report already acknowledges example false negatives (`docs/REPORT.md:278`). The seven-problem rescue subset was selected around Luna failures (`analysis/luna_rescue.py:8`); it omits p05, where Haiku-medium's main-ladder miss occurs (`docs/REPORT.md:178`). Perfect performance on that subset is not a neutral family comparison.

**Effect:** the observed sol61/Astra builder results survive this review. The rule "Haiku repairs when a flagship check fails" is a proposed policy, not a validated recovery path. Neither its conditional success rate nor its cost is measured for those builders. Fresh-call repair also does not test a native agent repairing within its existing context.

**Show it:** probe key `repair_exposure`; inspect the configuration tables cited above.

**Recommended fix:** describe the policy as untested on flagship failures. Before promoting it as evidence-based recovery, compare the same saved, genuinely failing builds across same-family and cross-family repairers, keeping the error report, context, acceptance test and budget fixed. Include Claude builders and fresh versus continuing-agent repair explicitly if the intended router uses both.

### 3. High for economic routing: Claude's "measured bill" is also list-based accounting, and cache/quota assumptions can select a different route

**Evidence:** `bench/run.py:115` and `bench/agentic/run.py:59` preserve `total_cost_usd`; that is faithful extraction. But all **24 available Claude result transcripts say `modelUsage.*.costBasis = "list"`**, not actual-charge provenance. Example: `cache/agentic_raw/agentic-2c4b9788bf7e6a9a53ee2217eaa6b492802a69a79922c2a3b967574846fc6c27.out:20`. `README.md:7` calls Claude dollars "what the Claude side pays", and `analysis/summarize.py:86`, `122` labels Claude measured beside Codex proxy. The report qualifies the CLI accounting (`docs/REPORT.md:215`, `230`), but the README's billing claim is stronger than the evidence. The available raw transcripts cover Haiku-low and Sonnet-medium repo calls, not every Claude row; do not extrapolate that provenance audit silently.

Codex conversion uses recorded token counts and `results/prices.json`, not quota or invoice measurements (`analysis/summarize.py:31-44`). The README explicitly assumes list-price ratios track quota (`README.md:12`); no measured remaining-quota debit supports that. A $0 entry in the Claude column establishes no Claude builder call, not zero total marginal cost or a proven quota-efficient choice.

Cache state materially changes rankings. The probe gives Luna-low **$0.000899/pass with observed cache versus $0.002251/pass with no Codex input cache**; Haiku-low's CLI figure is $0.001122/pass. Sol61-high similarly moves from $0.018615 to $0.041573/pass. The existing `cost_uncached()` deliberately leaves Claude unchanged (`analysis/summarize.py:39-44`), so this is a one-sided sensitivity, **not a matched cold-cache experiment**. Some of this limitation is already disclosed, particularly for stripped Luna.

**Effect:** pass counts are unaffected. The cost ranking and "Codex while quota remains" decision depend on a chosen billing objective and cache regime, not capability evidence alone. I did not prove the stored prices or cost arithmetic wrong, and did not fetch replacement current prices for this dated experiment.

**Show it:** probe keys `claude_recorded_cost_basis` and `function_rates`; compare the cited README language with the raw `costBasis`.

**Recommended fix:** call the figures "Claude CLI-reported cost" and "Codex token-price estimate"; preserve Claude `costBasis`, per-model usage, and cache-write TTL. Separate API list economics from actual account charges and subscription/quota use. Provide symmetric cache sensitivities before comparing a cold deployment with the warmed benchmark.

### 4. Medium-high: missing agentic evidence becomes zero tests added, and the claimed regrading guarantee is false

**Confirmed reporting bug:** `analysis/report.py:329-330` uses `all(...)` on an empty evidence list and then `sum(...)`, producing **0**. `results/agentic_tests.json` has no rows for Haiku-high, sol61-high or Astra-medium. Nevertheless `docs/REPORT.md:125`, `128-129` displays 0 test functions for them while also reporting that all 12 requested test files were written. The probe invokes the actual `tables_md()` renderer and reproduces these three false zeros. This can mislead a quality-based choice, including against Haiku-high; it affects both families' later additions.

**Evidence loss:** only **48/84 agentic runs** have committed transcripts. The 36 runs for those same three later configs have none. More fundamentally, the runner saves a diff **stat**, deletes the edited repo, and retains only summary grading results (`bench/agentic/run.py:114`, `119`, `122-128`). Even the available Codex `file_change` transcripts generally retain changed paths rather than the final file bytes. An agentic result JSON is not a regradable completion. This contradicts the broad "every other result set ... can be re-graded" statement at `docs/REPORT.md:217`.

**Effect:** original pass receipts can be described as recorded results, but those agentic outputs cannot be independently regraded from the committed cache as claimed. Missing evidence also prevents auditing the later Codex delegation counts and tool/context parity.

**Show it:** probe keys `agentic` and `missing_evidence_rendered_as_zero`; inspect the storage fields in the runner.

**Recommended fix:** render absent evidence as `unknown`, show evidence coverage, and avoid vacuous `all([])` aggregation. Save a scrubbed full patch/final repo plus raw call for each future run before cleanup. Narrow the current reproducibility claim; missing historical artifacts cannot be repaired by rerendering.

### 5. Medium on these results, high potential: hidden pytest can pass while executing no hidden tests

**Confirmed probe:** `bench/agentic/run.py:84-88` treats exit code 0 as success. `hidden_pass` is copied from it at `124`. A newly added `tests/conftest.py` can mark every `test_zz_hidden_*` item skipped. Pytest then exits 0. The harness checks only the original test file bytes for tampering (`106`, `110`), so this added hook does not enter that check.

The offline probe first runs an actual `assert False` hidden test, getting `ok=False, failed=1`. It adds the collection hook and reruns the **same** hidden test, getting **`ok=True, passed=0, failed=0`, `1 skipped`**. This is a grading bypass, not a hypothetical timing concern.

**Qualification:** all 84 recorded runs report at least six passed hidden tests. I found no recorded all-skipped run, so this probe does **not** establish inflated scores in the existing dataset. The source snapshots missing in finding 4 limit deeper audit. Also, `own_tests` only checks filename existence (`111-112`); a placeholder satisfies it, as the report mostly acknowledges.

**Show it:** probe key `hidden_skip_bypass`.

**Recommended fix:** require the expected hidden test IDs/count to execute and pass, rejecting skipped, deselected and xfailed hidden tests. Run trusted tests/configuration outside the model-controlled pytest configuration and retain the final source being graded. Regrade saved outputs where available; do not silently relabel the existing receipts.

### 6. Medium: changing host instructions or isolation can silently reuse the old completion

**Evidence:** function keys hash selected flags, prompt, CLI version and model/effort (`bench/run.py:84-89`); agentic keys add task files (`bench/agentic/run.py:37-42`). Neither records effective host instruction contents, resolved system/tool context or the relevant environment. The current host instructions demonstrably affect Codex behavior (finding 1). The probe switches two distinct scratch `CODEX_HOME` values while holding the version/prompt constant and obtains **the same key**. It never reads or creates credentials.

**Effect:** merely rerunning with a clean or changed home can return the old contaminated result at `bench/run.py:149-150` or `bench/agentic/run.py:93-94`. That could invalidate the very fairness ablation being proposed. This is a demonstrated identity collision; I did not find evidence that a past fairness run was actually corrupted by it. The deliberate phase omission that reuses escalation calls is separate and currently preserves five attempts per cell.

**Show it:** probe key `context_cache_collision`.

**Recommended fix:** version an explicit harness/isolation identity and include hashes of effective instruction/tool inputs. For a new isolation ablation use a new config/cache namespace, not only different environment settings. Keep historical records intact.

### 7. Medium, largely disclosed: effort labels and run schedules are not matched resource controls

**Evidence:** the same effort word is passed to both CLIs, but Luna-low averages **0 reasoning tokens**, Luna-medium **6.9**, and Haiku-low **1026.6** on L1–L6. Luna's high-effort pass count rises to **55/60** from 46/60 and 47/60; this directly changes what "skip Luna" should mean. The report already limits that recommendation to low/medium effort and documents the mismatch (`PLAN.md:123`; `README.md:21`). Those fixes are appropriate.

The later comparisons are also not randomized time blocks: all 60 Haiku-high calls use **2 lanes**, all 60 sol61-high calls **4**, Luna-high **1**. Haiku-high ran late on October 23/24, sol61-high earlier on October 23, and base configs on October 22. The probe preserves timestamps and lane counts. Configs occupy separate sequential lanes (`bench/run.py:189-196`), which also couples caching and elapsed time to schedule.

**Effect:** these are legitimate named-config measurements, but equal effort labels do not isolate family capability per unit of reasoning. Median cost/latency differences are observations from different load/cache periods, not controlled speed effects. I found no evidence that those schedules caused the observed correctness differences, and no reason to convert the quadratic p15 failures into passes.

**Show it:** probe key `function_rates`; compare its reasoning means, lane counts and timestamps.

**Recommended fix:** keep config-specific claims; for a new cross-family efficiency comparison, interleave matched task blocks and report success against measured latency/cost across effort levels. Do not call reasoning-token counts directly interchangeable across providers.

### 8. Medium for future runs, low demonstrated effect on current routing: budget and stop rules are not enforced as documented

| Defect and location | How to show it | Concrete fix |
|---|---|---|
| Function spend guard counts only `cache/calls` (`bench/run.py:92-98`, `152-156`); agentic adds its own directory (`bench/agentic/run.py:96-99`); appendix/trim callers bypass both (`bench/gated_repair.py:104-110`, `bench/plan_first.py:57-60`, `bench/trim_probe.py:91-94`). Report total sums function + agentic only (`analysis/summarize.py:277-283`). | Probe `spend`: function guard sees **$1.61278838**, agentic guard **$2.46239407**, while the five retained call directories contain **$2.78237032** of CLI-reported Claude cost. This is a lower bound on all historical experiment calls, not an exhaustive deduplicated invoice. README's $2.46 "Total spend" omits at least those separate cached appendix/trim calls. | Use a shared call-identity ledger covering every track. State the scope of reported totals. Do not sum pipeline output rows naively because builds/plans are shared. |
| Spend check and call are not an atomic budget reservation (`bench/run.py:153-159`; agentic has no lock). The CLI's `--max-budget-usd` is not supplied. | Two Claude lanes can both observe the same below-limit total before either writes a row. Static control-flow evidence; no paid concurrency probe was run. | Reserve bounded call budgets atomically and pass a per-call CLI ceiling; include in-flight work and persist failures. |
| The spend reader parses `.tmp` files too (`bench/run.py:95-96`), while other lanes write them (`170`). | Probe `inflight_spend_reader`: an incomplete `inflight.json.tmp` raises `JSONDecodeError`. | Read committed `.json` entries only and make ledger reads/writes concurrency-safe. |
| Quota flag does not stop the lane (`bench/run.py:167-172`, `192-194`), contrary to `PLAN.md:102`. | Probe `quota_lane`: real `main()` with a mocked quota response invokes the model stub **twice**, not once. The loop stops only on `refused`. Rate-limit failures have no separate lane stop either. | Return typed stop states for quota/rate limits; mark subsequent cells missing. |
| A subprocess timeout escapes without journaling a row (`bench/run.py:103`, `136`, `159-161`; agentic `47`, `66`, `108-119`), and there is no once-only harness retry promised at `PLAN.md:56`. | Probe `timeout_journal`: `TimeoutExpired` escapes `one()` and **zero rows** are saved. | Persist partial stdout/usage/error and the attempted identity before applying an explicit retry policy; report missing cells rather than silently losing attempts/spend. |
| Claude error classification ignores process return code (`bench/run.py:110`; `bench/agentic/run.py:60`); Codex includes it (`bench/run.py:139`; agentic `80`). | Probe `nonzero_exit_classification`: mocked exit 1 with a success-shaped Claude JSON is accepted, while Codex exit 1 is flagged. | Include `returncode != 0` in both Claude parsers and retain terminal-result provenance. |

No current function or agentic row has `is_error=True`. The last three defects are demonstrated failure-path risks, not evidence that this dataset's pass counts were altered. These guardrails also do not justify spending up to the nominal cap for this review: this review used **$0** of its separate $2 allowance.

## Fixes, commits and disposition

**Decided:** preserve the benchmark implementation and historical evidence. This review adds probes and recommendations rather than rewriting results or changing a harness underneath frozen measurements. No benchmark defect above is claimed fixed.

- Evidence/probe commit: **`6bd40f7`** (`review: add offline fairness and harness failure probes`). It contains `results/review-sol61/probe.py`, its captured JSON and the successful audit output.
- This document is committed in the following review commit; its hash is in the final receipt and `results/review-sol61/receipt.json`.
- Recommended implementation order: correct missing-as-zero and cost/provenance language; retain regradable agentic outputs and harden grading; repair cache/budget/error handling; then run a separately labelled, balanced native/delegation experiment. The flagship builder scores remain useful observations, while the native-family, same-family delegation and flagship-repair conclusions remain unresolved.

**Commit delivery limitation:** normal `git add` failed because this linked worktree's index lives under read-only `<repo>/.git/worktrees/mrb-sol61`. Commits were therefore created on a `review-sol61` branch in temporary Git metadata under `/tmp`, with the original `d94fbc8` parent and the current worktree files. `results/review-sol61/review.bundle` contains those commits for the orchestrator to import. The original worktree branch/ref and main were not advanced. The receipt records both the portable commit and the unchanged original HEAD; it does not claim a successful landing in the original Git metadata.
