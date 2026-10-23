# Pre-registration: experiment 2026-10-22b

Written and committed before any model call in this experiment. Changes after the first call are listed at the end under "Deviations", with the reason.

## Question

Which model and reasoning-effort setting should a router send a coding task to, given the task's difficulty? For each config: where does it stop passing, and what does a passing answer cost in dollars and seconds?

The pilot (`results/2026-10-22-pilot.jsonl`) could not answer this. All 205 runs passed, so the pilot found no failure points. Its problems were well-known LeetCode tasks.

## Configs

| id | CLI | model | effort |
|---|---|---|---|
| haiku-low | Claude Code | claude-haiku-5-5 | low |
| haiku-medium | Claude Code | claude-haiku-5-5 | medium |
| sonnet-medium | Claude Code | claude-sonnet-5-5 | medium |
| luna-low | Codex CLI | gpt-6-luna | low |
| luna-medium | Codex CLI | gpt-6-luna | medium |
| sol61-medium | Codex CLI | gpt-6.1-sol | medium |

Escalation configs (used only under the rule below): haiku-high, sonnet-high, luna-high, sol61-high.

Harness, the same for every config:
- Each CLI starts with user and project settings ignored: Claude `--setting-sources ""`, Codex `--ignore-user-config`. No host instruction files reach the model.
- Codex runs on `service_tier=default`.
- Each run gets a fresh temp working directory outside the home tree.
- Function track: Claude tools off (`--tools ""`), Codex read-only sandbox (its tools cannot be disabled), and the prompt says not to use tools.
- Agentic track: tools on for both families, with workspace-write permission.

## Function track: difficulty ladder

There are 10 problems on 5 rungs, 2 per rung. All were written for this benchmark on 2026-10-22, after every tested model's training cutoff, with new names, rules and I/O. The rung order below is my prior. The report shows the measured pass rate per problem next to it.

| rung | id | what makes it hard |
|---|---|---|
| L1 | p01 overlap_minutes | sweep line, half-open intervals |
| L1 | p02 squash | run-length encoding with an escape rule |
| L2 | p03 ledger | many interacting rules (freeze, undo, transfers) |
| L2 | p04 taller_within | n = 200,000, so an O(n·k) solution times out |
| L3 | p05 pass_route | shortest path where passes are bought at stations |
| L3 | p06 calc | expression semantics: truncating division, C-style modulo, `-2^2` |
| L4 | p07 weighted_distance_sums | rerooting on trees with n = 200,000, where recursion depth breaks naive Python |
| L4 | p08 recur | calendar recurrence: skip rules, Monday week anchor, nth weekday |
| L5 | p09 k_machine_schedule | max-weight intervals on k machines, where greedy fails |
| L5 | p10 avoid_count | strings avoiding patterns for n up to 10^18 |

Grading for each problem:
- An efficient reference and an independently written brute force must agree on at least 2,000 random small inputs.
- At least 2 planted wrong solutions (greedy, off-by-one, too slow, missed rule) must fail the checker.
- `make selftest` enforces all of the above.
- Candidates run in a separate `python3 -I` process with CPU and memory limits.
- Time limit: max(2 s, 10 × the reference's time on the same input), on large cases only.
- Grading runs serially, after generation, so parallel lanes cannot cause false timeouts.

Each run gets one of these outcomes: `pass`, `wrong`, `timeout`, `crash`, `no_code` or `harness_error`. Only `pass` counts as a pass. Runs ending in `harness_error` are re-run once; if a run fails again, it is reported and counted as a fail.

## Agentic track

There are 4 small multi-file Python repo tasks. Each has visible tests and hidden tests; the hidden tests are copied in only after the agent exits.
- Configs: haiku-low, sonnet-medium, luna-low, sol61-medium.
- 3 repeats each.
- Reported: hidden-test pass rate, visible-test pass rate, wall time, tokens, $.

## Metrics

- pass@1: the fraction of single attempts that pass, with no retries and no answer selection.
- 95% CI: hierarchical bootstrap with 10,000 resamples. Each resample draws problems, then repeats within each problem, so repeats of one problem are not treated as independent.
- Config-vs-config differences: paired on the same problems.
- Latency: median and p90 wall-clock seconds per call, pooled over all runs of a config. A single cell (n = 5) gets a median only.
- Tokens: input, of which cached, and output, of which reasoning.
- Cost: mean $ per run and $ per passing run (total $ ÷ passes).
  - Claude: the CLI's measured `total_cost_usd`.
  - Codex: a proxy, raw token counts × the per-model list price from the most authoritative source I can verify, with its URL and access date recorded in `results/prices.json`. The report labels these figures "proxy".
- Breaking point of a config: the lowest rung whose pooled pass@1 is 40% or less (at most 4 of 10 runs). A config that never drops that low has no breaking point within the ladder ("none ≤ L5").

## Hypotheses (stated before data)

- H1: Every base config scores at least 80% on L1 and L2. Easy tasks do not separate the models.
- H2: Within each model, higher effort moves the breaking point up by at least one rung, or removes it.
- H3: Among configs with 100% pass on L1–L2, luna-low has the lowest $ per passing run on those rungs.
- H4: At least one config has a breaking point at or below L5. If none does, the ladder failed at its purpose, and I report that.
- H5: On the agentic track, under matched clean harnesses, Codex's minimum input tokens per run are higher than Claude's.

## Run plan and stop rules

1. Warm-up: one call per config on p01, discarded (phase `warmup`). It absorbs the first-call prompt-cache write.
2. Calibration: 1 repeat of haiku-low, sonnet-medium and sol61-medium on all 10 problems.
   - If sonnet-medium and sol61-medium both pass both L5 problems, I write 2 harder problems (L6), self-test them and add them, once only, before the main run.
   - Calibration rows count as repeat 0 and are not pooled into the main estimates.
3. Main run: 6 base configs × 10 problems × 5 repeats = 300 calls.
4. Escalation, one step at most: if a model's highest base effort scores 2/5 or less on a problem, that model's next effort level (haiku-high, sonnet-high, luna-high, sol61-high) runs 5 repeats on those problems only. It is compared with the base config on that subset only, never pooled into the full-ladder Pareto chart.
5. Agentic track: 4 configs × 4 tasks × 3 repeats = 48 calls.

Concurrency:
- At most 4 lanes.
- One config per lane, with calls sequential within a lane.
- The concurrency level is recorded in the run manifest.

Budget:
- The runner sums Claude `total_cost_usd` from the cache ledger and refuses new Claude calls once the total passes $8.00. The hard ceiling for the task is $10.
- If Codex returns a quota or rate-limit error, Codex lanes stop, the exact error text goes into the manifest, and those cells are reported as missing.

Caching:
- Every model call is stored under `cache/` with the key sha256(config, model, effort, CLI version, harness flags, prompt, problem, repeat).
- A re-run with the same key returns the stored completion and makes no model call.
- Grading and reporting read only the cache and `results/`.

## Deviations

Each entry gives the change, when it happened, and why.

1. Codex harness: the plan's flags (`--ignore-user-config`, default service tier) were extended with `-c skills.include_instructions=false`, before the first model call. Without it, Codex injects the host's skill list (about 5.6k input tokens) into every prompt.
2. Codex harness, limitation: Codex still injects the user-level `AGENTS.md` (about 1.3k tokens of host-specific instructions). No CLI flag disables it, and the alternative (a separate `CODEX_HOME`) would mean copying the login credentials. Codex input-token floors therefore include about 1.3k tokens that a clean install would not have. This affects H5 and the token-floor chart.
3. Claude agentic harness: tools are pinned to `Bash,Read,Edit,Write,Glob,Grep` and `--strict-mcp-config` is added, before the first agentic call. The default tool set adds remote connectors and built-in skills (about 31k input tokens); the pinned set matches what Codex's shell and edit tools can do.
4. Warm-up rows use repeat number 100 rather than -1 (a CLI parsing limitation). They are excluded from every estimate.
5. Calibration result: haiku-low, sonnet-medium and sol61-medium passed all 10 problems (30/30, one repeat each). The L6 rule fired. I wrote `p11_best_average` (exact fraction, near-tie cases that defeat floating point) and `p12_sheet` (spreadsheet evaluator with lazy IF, left-to-right error short-circuit, cycle detection, deep reference chains). Both passed the checker self-test (reference = independent brute force on 2,000 random inputs; every planted bug fails). They were committed before any model saw them, and were not tried on a model and revised. The main run becomes 6 configs × 12 problems × 5 repeats = 360 calls. If L6 does not break any config either, the ladder stops there: no L7.
6. Analysis code (`analysis/`) was written in this session, not delegated to a separate Codex lane, so that no more than 4 model processes ran while calls were being timed.
7. The Claude agentic harness uses `--output-format stream-json --verbose`, so tool calls can be counted. The function track keeps `--output-format json`.
8. Added after the main run, at the operator's request, and labelled exploratory everywhere: `bench/trim_probe.py`. It measures the Codex input-token floor as config knobs are switched off, one call per level on a pilot problem, then 3 rounds × the 3 pilot problems for gpt-6-luna and gpt-5.6-terra at three levels against haiku-low with tools off. Its leanest level ("noshell") then ran the full 12-problem ladder as `luna-low-bare` (phase `exploratory`, 5 repeats). None of this changes a pre-registered estimate or hypothesis.
9. Deviation 2, checked directly: with `--ignore-user-config` and `project_doc_max_bytes=0`, Codex still quotes an `# AGENTS.md instructions` block, and the token count does not change. That block comes from the global instruction file under the Codex home directory. Removing it needs a separate `CODEX_HOME`, which means copying or linking the login file. I did not do that, because this benchmark does not handle credentials.
10. The escalation rule fired once: luna-medium scored 2/5 or less on p04, p11 and p12, so luna-high ran 5 repeats on those three problems.
11. After a methods review, and labelled exploratory: luna-high on all 12 problems, 5 attempts each. At low and medium effort luna emits almost no reasoning tokens while haiku-low emits about 1,000 per call, so "low" is not the same reasoning budget on both CLIs. The 15 escalation calls on p04, p11 and p12 have the same cache keys and are reused.
12. Deviation 2 also changed behaviour on the agentic track, not only token counts. Of the shell commands Codex ran there, 57 of 97 (sol61-medium) and 26 of 62 (luna-low) mention `AGENTS.md`, call a host tool that the host's `AGENTS.md` names, or clean up that delegate's `artifacts/` directory; the count comes from the `HOST_DOC` pattern in `analysis/agentic_tests.py`. An earlier version of this line said 50 for sol61-medium, a hand count that could not be reproduced. They come from host instructions, not from the task. Removing them needs a scratch Codex home holding the CLI's login file. That means handling credentials, so it was not done, and the agentic latency and token numbers for Codex include this overhead.
13. The message of commit 7895026 says the L6 problems were frozen "before any model call". The precise statement is that they were frozen before any model saw them: the calibration run on L1–L5 (deviation 5) came first.
14. Analysis changes after the review, made before the README was final: the Pareto frontier is computed on ($ per pass, pass@1), not ($ per pass, latency); the escalation comparison is reported as counts with no interval; and when every attempt passes, the lower bound is 0.05^(1/m) over the m problems or tasks rather than over attempts.
15. Two inputs are not in the cache keys. The one-line Codex system prompt (`bench/pilot/min_instructions.txt`) and the grader source (`bench/grade.py`, `bench/sandbox_exec.py`) are pinned by hash instead. A changed file stops the runner or grader rather than silently reusing cached results.
16. After the report, at the operator's request: a seventh rung. sonnet-medium passed 60/60 and sol61-medium 58/60, so L1–L6 no longer shows where the strongest configs break. I wrote three L7 problems and committed them, self-tested, before any model saw them: `p13_xor_ring` (a linear cellular automaton on a ring run for up to 10^18 steps; simulation and cycle detection time out), `p14_bounce_board` (exact expected turns on a board with bounce-back and chained jumps, or `None` when the game may never end; a solve over unreachable cells goes singular), and `p15_paint_erase` (range max-paint and erase on 10^9 cells; walking an interval map is quadratic on one test). Before freezing, I checked that a list-based solution for p13 and a chronological lazy segment tree for p15 pass inside the time limits, so the limits do not demand my particular method. L7 runs on sonnet-medium, sol61-medium, haiku-low and luna-high, 5 attempts each, under phase `hard`, and is reported separately: the L1–L6 estimates, breaking points and hypotheses do not change. Claude budget for this step: $3.
17. After the report, at the operator's request: code-quality measurements of the graded solutions, as extra columns. Pass/fail stays the headline and nothing is folded into one score. `make quality` (needs `uvx`; no model calls; not part of `make report`) writes `results/quality.jsonl`, one row per non-warmup call, and `results/quality_meta.json` with tool versions (radon 6.0.1, ruff 0.17.1, Python 3.12.3), sizes and reference timings. Every solution is exported, byte-identical to the graded code, under `results/solutions/` by `make solutions`.
    - **Static, every completion with code.** `loc`: non-blank, non-comment lines by tokenizer (docstrings count). `cc_max`, `cc_total`: radon cyclomatic complexity per function, method and closure. `lint_warnings`: `ruff check --isolated --select E,F,W,B --ignore E501`.
    - **Time growth, passing completions only.** Each problem has a generator `sized(n)` in `bench/quality/sizes.py` whose work scales with one parameter (for example the number of operations for p15, using the comb worst case, and the week gap K for p08). The candidate and the reference run at n0, 2n0, 4n0 and 8n0 in the grader's sandbox, fastest of 3 repeats, killed above 10 s. `time_exp` is the least-squares slope of log time on log n; `time_ratio` is candidate over reference time at the largest size both finished. Outputs are compared with the reference's at every size. The report counts a solution as growing worse than the reference when its exponent is more than 0.3 above the reference's.
    - **Memory, passing completions only.** tracemalloc peak of the call at 4n0, candidate over reference, in a separate run.
    - **Caveats.** One timing run on a shared host. Slopes come from four points over an 8× range, and where a statement caps n the call takes under 5 ms at n0 and the slope is noisy (314 of 513 measured rows carry that note). The generators are mine, not pre-registered, and each is one input family. tracemalloc misses the input, interpreter overhead and C-level allocations. LOC, complexity and lint describe the text; they are not judgments of quality.
18. Exploratory appendix arms B1, B2, C, D and E were run ad hoc after the main run. Their prompts, flags and CLI versions were not kept, so `results/appendix/luna_rescue.jsonl` contains graded rows only and they cannot be re-graded. Arm E is reproduced from committed code by `bench/gated_repair.py` config `luna-low+haiku-review-all`; its review prompt is a reconstruction. Arm D's luna-high-bare builds are reproduced by the gated-repair builds. Arms F (`bench/plan_first.py`) and G (`bench/gated_repair.py`) are fully cached.
19. 2026-10-23, at the operator's request and after the results were known: four more Codex configs with the stock harness, phase `exploratory` on L1–L6 and phase `hard` on L7, 5 attempts each: `sol56-high` (gpt-5.6-sol), `luna56-low` and `luna56-high` (gpt-5.6-luna), and `astra-medium` (gpt-6-astra). `gpt-6-sol` (superseded by gpt-6.1-sol) and `gpt-5.6-terra` (sol's price tier, seen in the pilot) were left out. Prices for the two gpt-5.6 models were added to `results/prices.json` from their model pages. They are reported apart ("More Codex models") and do not change the pre-registered comparisons; the L7 claims about the first four configs are scoped to them.
