# SHRINK-PLAN-2: the report generator (2026-11-08)

Outcome: [SHRINK-REPORT-2.md](SHRINK-REPORT-2.md). Stage 3 (freeze) was dropped and stage 4 came in far below budget; this plan is kept as written before the build, apart from the recorded freeze decision.

Phase 1: `SHRINK-PLAN.md` and `SHRINK-REPORT.md` at commit 7e946a6. Baseline for this plan: main at 7e946a6.

## What the trace found
Method: a `sys.monitoring` line tracer over `analysis/*` while running the whole `make report` and `make audit` module chain; then a key-by-key check of facts against templates and Python readers.

1. **Dead branches are not the win.** `dataset.py` has 1,684 executable lines and 1,670 ran; `summarize.py` 536 of 537. Whole functions that never run: `charts.explorer_panels`, `explorer_radars`; `page.pass_cost`, `pack_zero_lane`, `hard_pass_cost`, `hard_speed_cost`, `l7_reason`, `sets_box`, `rescue_subtitle`, `speed_frontier_text`; `harness_bias.fill_cost`, `claude_rows`, `codex_rows`, `main`; `rawindex.supporting`. About 300 lines.
2. **The code is prose.** `_facts` alone is 552 lines and 55.8 KB. It builds 736 facts, most of them finished sentences with numbers in them, and 171 `need()` lines assert that the wording still matches the data. Lines average 81 bytes, some over 1,000. The generator already is dense, so **line count alone is a bad metric here**: every budget below is lines and bytes, and joining lines to hit a budget is not allowed.
3. **Unused output is locked.** 263 of the 736 facts (43 KB of `dataset.json`) reach no template and no Python reader. They exist only as bytes in `results/dataset.json`, which is a committed output, so they cannot be dropped under the byte rule. Same for parts of `dataset.json`'s `report` block. Facts the page uses are also locked by name: the page embeds them in its data block.
4. **The page is 732 KB, not 100 KB**; `dataset.json` is 4.6 MB (2.5 MB of it `explorer`). It bears on any claim about "one small page".

So a byte-identical "few hundred lines" generator does not exist unless the sentences move somewhere else. Going much below 6,500 lines means no longer deriving the text. See "Freeze" and its limit.

## What each page section needs
| Section | Tokens (facts + widgets, tables, charts) | Population | Plan |
|---|---|---|---|
| Winner | 14 + `winner` | open: new configs | live |
| Cost vs accuracy | 1 + `explorer` | open | live |
| Results | 6 + `fast`, `full_table`, `result_notes`, `short_table` | open | live |
| Problems | 1 + `problems` | open | live |
| How it was run | 25 + `legend` | open | live |
| Where they fail | 6 + `grid` | open | live |
| Baseline input tokens | 1 + `floor` | open | live |
| Other measures | 12 + `agentic`, `t1_regrade`, `any_pair` | open | live |
| Conclusion, Limitations | 21 | open; mostly `need()`-guarded prose | live |
| Codex vs Claude | 7 + `equiv_all` | open | live |
| Interesting findings | 9 | mixed | live |
| Grok and Devin | 19 + 11 tables + `grok_summary` | mixed: equivalence and closest-lane tables are open; Devin and repo comparison look closed | keep open parts live; freeze only what passes the checks |
| Pipelines | 5 + `pipes` | mixed: `rescue` moves under mutation; arm rows look closed | live unless the checks pass |
| Whose bench? | 24 + `harness_bias.svg` | looks closed | freeze if the checks pass |
| Code quality and evidence | 58 + `blind`, `quality`, `everything` | pilot, trim, quality look closed; `everything` open | freeze parts that pass the checks |

## Freeze: dropped, measured
The first plan froze closed sections into `results/frozen.json`. It is dropped. A scripted prototype in `_facts` removed 196 lines and froze 194 of the 517 facts that did not move under seven mutations. With the rest of the closed-arm code it might reach about 450 lines net of its own machinery (about 6% of the code). In exchange those numbers stop being derived, and `make audit` only checks a hash on them. `README.md` says its commands "rebuild committed data"; that sentence would become partly false, and `README.md` is locked by the golden. So this goes under "left undone". Details in the report.

## Gates beyond `tools/gate.sh`
The gate compares the tree to HEAD. A regenerated file committed along with a change would pass it, so it cannot prove outputs unchanged.
1. **Baseline diff.** The gate also runs `git diff --quiet 7e946a6 HEAD -- results/report results/dataset.json results/manifest.json README.md docs/REPORT.md docs/RAW_RUNS.md results/solutions` and prints `BASELINE-SAME`. All outputs stay byte-identical to 7e946a6, `dataset.json` included.
2. **Differential mutation.** Golden bytes prove only today's data. Before each generator stage lands, the old (7e946a6) and new generators run on the same mutated rows (a new config in a new results file; one flipped pass; changed tokens; a changed price, all on configs that no `need()` names). Their `dataset.json` and `page.html` must match, apart from frozen keys; "both raise" counts as a match only with identical messages. This catches a rewrite that fits today's data and breaks on tomorrow's.
3. **Runner smoke.** Fake CLIs that report the cached version, as in phase 1: `bench.run` 120/120, `bench.agentic.run` 66/72 (6 known `t1_discount` misses, baseline behaviour), results unchanged.
4. **Guards stay.** `need()` tripwires, audit literal scan, and page guards stay for all live sections. A `need()` goes only with the sentence it guards.

## Line budget (lines / KB, code only)
Counter: `git ls-files` for `analysis`, `bench`, `tools`, `Makefile`, excluding `bench/problems`, `bench/agentic/tasks`, `bench/pilot` (the report gives the exact command).

| File | Now | Target |
|---|---|---|
| `dataset.py` | 1,997 / 162 | 1,350 / 110 |
| `page.py` | 1,339 / 87 | 1,100 / 72 |
| `charts.py` | 715 / 48 | 600 / 40 |
| `summarize.py` | 685 / 46 | 520 / 35 |
| `grok.py` | 495 / 32 | 420 / 28 (equivalence matching stays live) |
| `terra_priority.py` | 225 / 14 | 0 if it passes the freeze checks, else 200 |
| `harness_bias.py` | 199 / 9 | 40 / 2 (the helpers still read) |
| `fast_gate.py`, `luna_rescue.py` | 155 / 8 | 60 / 3 |
| `run.py` | 495 / 27 | 300 / 16 (drop the retired Grok, Devin, Hetzner callers) |
| `agentic/run.py` | 271 / 17 | 200 / 13 |
| everything else | about 1,900 | about 1,700 |
| **Total** | **8,446 / 549** | **about 7,500 without the freeze** |

That misses both the phase-1 ceiling and the operator's bar (a few hundred). Going further needs an output change or a freeze; neither is in scope.

**Docs.** Phase 1's counter (`tools/count.sh`: `*.md` and `docs/*.json` outside `results`, `cache`, design system) reads 3,163 now. `docs/landcheck_allow.json` is 747 of that, and most entries acknowledge removals already landed on main, so they no longer match anything. Trim those and `docs/SETUP.md`. The floor under this counter is about 2,090: generated and byte-locked `REPORT`, `README`, `RAW_RUNS` (865), their templates (949), `PLAN.md` (152, cited), task and pilot markdown (about 97), `audit_allow` (27). **So under 2,000 cannot be met without an output change.** The report gives the counter's number, plus the number without generated files. The counter does not change.

## Stages (each one PR, gated, reviewed by a Claude model named in the PR)
1. **Gate and dead code.** Add baseline diff to the gate; delete the never-run functions. About -300.
2. **Runner.** Drop `call_grok`, `call_devin`, `call_hetzner` and their guards: no `bench.run` call for those lanes in 30 days (transcript grep hits are imports of `CALLS`), and no pending deviation in `PLAN.md`. Keep: `CONFIGS`, all flag lists, `key_for` byte for byte, `CLAUDE_BUDGET_USD` and the Claude guard, `isolated_codex_env`, the `MIN_INST` hash check, raw stdout writing (the analysis imports and the manifest need these). Runner smoke before and after. The optional `make grade` refusal goes here. About -270.
3. **Freeze:** dropped, see above.
4. **Dedupe live code.** Shared helpers, pure refactors, differential mutation per file; fact order preserved. About -500. Stop at the first file that fails twice.
5. **Docs.**
6. **Report, lesson, bus post.** Full-freeze option written up as undone, never built.

## Rollback
Each stage is one merge commit; `git revert -m 1`. Tag `pre-shrink-2` at 7e946a6, local only. The page is byte-identical, so nothing live changes at any stage; after the final push, check live page sha == main.

## Off limits
Tags `pre-shrink`, `ruling/f77c040`, `dbench/*`, `shrink-1101`, sibling checkouts: untouched. No history rewrite, no force-push.
