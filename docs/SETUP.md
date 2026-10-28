# Benchmark setup

Rebuild the report from committed rows. Run models only when you want new measurements.
The [raw run index](RAW_RUNS.md) links the data in place and records hashes.
The [plan](../PLAN.md) records the original design and dated deviations.
The [full report](REPORT.md) gives findings and limitations.

## Models and lanes

The [manifest](../results/manifest.json) records model IDs, effort, CLI versions and harness flags.
The [config registry](../analysis/configs.py) separates the main ladder, exploratory runs, pilot and appendix arms.
These are recorded settings, not claims about current vendor offerings.

| Lane / config family | Exact model ID | Recorded effort levels | Scope |
|---|---|---|---|
| Claude / `haiku` | `claude-haiku-5-5` | low, medium, high | Main, escalation, exploratory, repo tasks, pilot, repair |
| Claude / `sonnet` | `claude-sonnet-5-5` | medium; low in pilot | Main, repo tasks, pilot |
| Codex / `luna` | `gpt-6-luna` | low, medium, high | Main, escalation, exploratory, trim, repo tasks, pilot |
| Codex / `sol61` | `gpt-6.1-sol` | medium, high, xhigh; low in pilot | Main, exploratory, repo tasks, pilot |
| Codex / `luna56` | `gpt-5.6-luna` | low, high | Exploratory |
| Codex / `sol56` | `gpt-5.6-sol` | high | Exploratory |
| Codex / `astra` | `gpt-6-astra` | medium; low in pilot | Exploratory, repo tasks, pilot |
| Codex / `terra` | `gpt-5.6-terra` | low | Pilot and trim probes |
| Codex / `sol6` | `gpt-6-sol` | low | Pilot only |
| Grok / `grok47` | `grok-4.7` | low, medium, high | Staged function run; repo tasks at low and high |
| Grok / `grok47fast` | `grok-4.7-build-fast` | low | Staged function run |

The six pre-registered base configs are `haiku-low`, `haiku-medium`, `sonnet-medium`,
`luna-low`, `luna-medium` and `sol61-medium`.
Higher efforts, stripped harnesses, fast mode, repair pipelines and later models are separate exploratory comparisons.
Effort labels do not imply equal reasoning-token budgets across CLIs.
The `-fast` Codex configs use priority service at the same model and effort.
Grok's `grok-4.7-build-fast` is a distinct model ID.
Pilot `codex-*` names map to `gpt-6.1-sol`; see the registry for display aliases.

| CLI | Versions in the manifest | Track behavior |
|---|---|---|
| Claude Code (`claude`) | 2.1.308 | Function tools disabled; repo tools pinned to Bash, Read, Edit, Write, Glob, Grep |
| Codex CLI (`codex`) | 0.163.0, 0.164.0 | Function read-only sandbox with a no-tools prompt; repo tasks use workspace-write |
| Grok CLI (`grok`) | 1.0.70 | Function tool allow/deny flags; repo tools enabled, web and subagents disabled |

The [Codex-designed harness](../bench/codex_harness.py) is a separate appendix intervention.
It lets both families implement `solution.py`, run checks and revise within one session.
Its source records validation against Codex 0.163.0 and Claude 2.1.293.
Per-row `cli_version` fields remain the record of each actual call.

## Task sets

The [function problems](../bench/problems/) contain statements, signatures, references,
independent brute-force implementations, test generators and planted wrong answers.
Rungs express the author's prior about difficulty.

| Rung | Problem | What it tests |
|---|---|---|
| L1 | [p01 overlap_minutes](../bench/problems/p01_overlap_minutes.py) | Sweep line with half-open intervals |
| L1 | [p02 squash](../bench/problems/p02_squash.py) | Run-length encoding and escaping |
| L2 | [p03 ledger](../bench/problems/p03_ledger.py) | Freeze, undo and transfer rules |
| L2 | [p04 taller_within](../bench/problems/p04_taller_within.py) | Scalable bounded-window search |
| L3 | [p05 pass_route](../bench/problems/p05_pass_route.py) | Shortest paths with station-bought passes |
| L3 | [p06 calc](../bench/problems/p06_calc.py) | Parsing, precedence and integer arithmetic semantics |
| L4 | [p07 weighted_distance_sums](../bench/problems/p07_weighted_distance_sums.py) | Tree rerooting and deep trees |
| L4 | [p08 recur](../bench/problems/p08_recur.py) | Calendar recurrences, skip rules and weekday anchors |
| L5 | [p09 k_machine_schedule](../bench/problems/p09_k_machine_schedule.py) | Weighted interval scheduling on several machines |
| L5 | [p10 avoid_count](../bench/problems/p10_avoid_count.py) | Pattern avoidance at very large lengths |
| L6 | [p11 best_average](../bench/problems/p11_best_average.py) | Exact fractions and near ties |
| L6 | [p12 sheet](../bench/problems/p12_sheet.py) | Lazy spreadsheet evaluation, error order, cycles and deep chains |
| L7 | [p13 xor_ring](../bench/problems/p13_xor_ring.py) | Ring automata at very large step counts |
| L7 | [p14 bounce_board](../bench/problems/p14_bounce_board.py) | Exact expected turns, chained jumps and nontermination |
| L7 | [p15 paint_erase](../bench/problems/p15_paint_erase.py) | Large range paint/erase and adversarial update cost |

L1–L5 were the original ladder. Calibration passed every problem and triggered the planned L6 extension.
The main ladder is p01–p12, normally five attempts per config.
Warmup and calibration rows stay in the data but are excluded from main estimates.
The hard set is p13–p15 at L7. It was added after the report, uses selected configs,
and is reported separately. See deviations 5 and 16 in the plan.

The [pilot](../bench/pilot/README.md) used FizzBuzz, Course Schedule II, Candy,
Reconstruct Itinerary, Minimum Window Substring and Wildcard Matching.
They test basic branching, graph order, allocation, traversal, sliding windows and pattern matching.
All 205 function attempts passed. These familiar problems did not reveal failure points.
The pilot repo task added invoice discounts with builder/reviewer pipelines.
Its small sample and historical harness differ from the main run.

| Repo task | What it tests |
|---|---|
| [t1_discount](../bench/agentic/tasks/t1_discount/TASK.md) | Discount rounding and validation across money, store and CLI modules |
| [t2_cache_bugs](../bench/agentic/tasks/t2_cache_bugs/TASK.md) | TTL boundaries, LRU updates, expiration and statistics |
| [t3_config_refs](../bench/agentic/tasks/t3_config_refs/TASK.md) | Nested references, escaping, cycles and error attribution |
| [t4_retry_queue](../bench/agentic/tasks/t4_retry_queue/TASK.md) | Retry backoff, queue order, exception handling and counters |

Repo tasks normally use three attempts per config, visible tests and hidden tests.
The staged Grok function run covers p01–p06 with a stop rule, not the full ladder.
Its L1 uses five repeats; L2–L3 were shortened to two with existing extra repeats retained.
Grok repo tasks use two repeats. See deviations 21–22.

## Grading

[bench/grade.py](../bench/grade.py) compares function outputs against the reference on fixed,
seeded random and large cases. [bench/sandbox_exec.py](../bench/sandbox_exec.py) loads the
candidate in a separate isolated Python process and records outputs, errors and timings.
CPU and memory limits apply. Large-case limits scale with reference time.
Generation finishes before serial grading, so model-call concurrency does not compete with timed cases.
Only a complete pass counts. Wrong answers, timeouts, crashes, missing code and harness errors remain explicit outcomes.

`make selftest` checks reference/brute-force agreement and rejects planted wrong answers.
It makes no model calls. It is separate from the faster analysis tests.

[bench/agentic/run.py](../bench/agentic/run.py) gives the agent a throwaway task repo.
Hidden tests enter the grading process only after the agent exits.
See the [hidden tests](../bench/agentic/tasks/t1_discount/hidden/) and each task's sibling `hidden/` directory.
The runner checks visible and hidden outcomes, added tests and test tampering.
New runs retain candidate patches. Older verdict-only repo runs cannot be re-graded from their caches.
Hidden pytest imports candidate code; it is outside the function grader's resource sandbox.

The report uses pass@1 and hierarchical bootstrap intervals over problems, then repeats.
Perfect results use a lower bound based on the number of problems or tasks.
See the plan and report for the statistical definitions.

## Prices and accounting

[results/prices.json](../results/prices.json) stores USD per million tokens, source URLs and verification dates.
Its access date is 2026-10-22; the gpt-5.6-luna and gpt-5.6-sol entries were verified on 2026-10-23.
Sources are OpenAI's developer pricing page and per-model pages, as recorded in that file.
These are historical benchmark inputs.

| Provider | Cost in this benchmark |
|---|---|
| Claude | CLI-reported `total_cost_usd` |
| Codex | Uncached input, cached input and output tokens at the recorded list prices; an estimate |
| Codex fast mode | 2× the applicable model rates at the same effort |
| Grok | CLI-reported `total_cost_usd` |

Codex subscription calls consume quota. List-price estimates are not invoices.
Claude spend is tracked separately from Codex estimates.
The pilot's old 1.5× priority estimate is repriced at 2× by analysis.

## Host and cache behavior

The standard runners use fresh working directories and ignore user/project settings.
Historical Codex runs still loaded user instruction text despite those flags.
This affected token floors and repo-task behavior; deviations 1–3, 9 and 12 document it.
[bench/isolated.py](../bench/isolated.py) reruns selected cells with a fresh Codex home,
using [bench/codex_env.py](../bench/codex_env.py) for the isolated environment.
Historical rows remain separate. See the report for the retained function comparison and clean-home repo reruns.

[bench/codex_harness.py](../bench/codex_harness.py) adds a separate Bubblewrap filesystem allowlist,
a synthetic HOME and read-only authentication mounts. It hides host instructions and prior answers.
It needs Linux, Bubblewrap/user namespaces and the chosen CLIs.
Its code-execution intervention differs from the original function track.
Shell network access is not technically blocked; the prompt prohibits external lookups.

Successful calls are cached by keys covering configuration, model, effort, CLI version,
harness flags, prompt, problem and repeat. Repo-task keys also cover task trees.
Rerunning the same successful keys reuses the cache with no new model charge.
New keys and retries after infrastructure errors can make paid calls.
The plan records inputs pinned by source hash instead of included in keys, and the trim probe's remaining omissions.

The main commands use `--lanes 4`: at most four calls in flight, sequential within each lane.
CLI wall time includes startup and network latency.
Some exploratory runs used one lane at another time of day.

## Rerun commands

Use Python 3.12.3 and the pinned dependencies in [requirements.txt](../requirements.txt).
Offline reporting needs no model CLI or model credentials.
Run these from the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
make report
python3 -m analysis.raw_runs --check
python3 -m pytest -q tests
python3 -m analysis.audit
python3 -m analysis.landcheck --base main
```

`make report` rebuilds derived results, charts, the README, report, page and raw run index.
It does not regenerate historical grades. `python3 -m analysis.raw_runs` updates just the index.
The [Makefile](../Makefile) is the command reference.

| Command | Effect | New model cost? |
|---|---|---|
| `make report` / `make audit` | Rebuild / verify offline analysis | No |
| `make selftest` | Validate reference checkers and planted bugs; about 12 minutes | No |
| `make grade` | Grade/export cached completions and repo verdicts | No |
| `make solutions` | Export graded answers | No |
| `make quality` | Static, growth and memory measurements; needs uvx, radon and ruff | No model calls |
| `make run` | Main function configs, five repeats, four lanes | Yes, for uncached calls |
| `make hard` | Selected L7 configs, five repeats, four lanes | Yes, for uncached calls |
| `make agentic` | Repo tasks, three repeats, four lanes | Yes, for uncached calls |
| `make escalate` | Planned conditional effort escalation | Yes, for uncached calls |
| `make trim` | Harness floor and paired probes | Yes, for uncached calls |
| `make plan-first` | Appendix F plans and builds | Yes, for uncached calls |
| `make gated-repair` | Appendix G builds and conditional repair | Yes, for uncached calls |

For example, `make run RUN_CONFIGS=haiku-low,luna-low` narrows the configs.
`HARD_CONFIGS` and `AGENT_CONFIGS` override the other tracks.
Model runs require the corresponding authenticated CLI; executable overrides are `CLAUDE_BIN`, `CODEX_BIN`, `GROK_BIN`.
Budget and quota stop behavior is documented in the plan and runner.

## Known limits

- Small samples give wide intervals. Rung order is a prior, and the breaking point is unstable.
- All 84 original repo runs passed hidden tests; 83 passed visible tests. In [the results](../results/2026-10-22b-agentic.jsonl), `luna-low` on `t2_cache_bugs`, repeat 2, has `visible_pass: false`. They separate cost and latency, not capability.
- Timings come from one shared host and include CLI/network overhead. They are not API time-to-first-token.
- The original function track asks for one answer without tools. Codex cannot disable its tools fully; read-only mode and the prompt constrain it.
- Sandbox policies differ between CLIs. The separate Codex-designed appendix allows checks and revisions.
- Subscription quota, list-price proxies and provider prompt caching make cost comparisons conditional.
- L7, added models, full-ladder high effort and repair arms are exploratory. They do not revise pre-registered hypotheses.
- Pilot and original appendix B1–E rows lack full call provenance for re-grading. Arms F and G retain caches.
- Quality metrics describe text and selected generated inputs. Growth slopes and memory measures have the limits recorded in deviation 17.
- Hosted models and CLI behavior change. Later runs can differ even with the same task files.
