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
