# Shrink report, phase 2: the report generator (2026-11-08)

**Result: not reached.** Code fell 7%, from 8,446 to 7,865 lines. That is above the phase-1 ceiling of 6,500 and far above the operator's bar of a few hundred. Docs fell to 2,457 lines, still above 2,000. Every committed output is byte-identical to 7e946a6. The rule that keeps the outputs byte-identical is what stops it going lower.

Landed as PRs #2, #3, #4, #5 and #6. Phase 1's plan and report are at commit 7e946a6 (`SHRINK-PLAN.md`, `SHRINK-REPORT.md`).

## Line counts

`tools/count.sh` uses phase 1's counter. Baseline is 7e946a6.

| | Before | After |
|---|---|---|
| Code, lines | 8,446 | 7,865 |
| Code, bytes | 549,296 | 515,472 |
| Tests | 884 | 884 |
| Page source, not counted as docs | 1,174 | 1,174 |
| Docs (`*.md` and `docs/*.json`) | 3,163 | 2,457 |
| Docs that are generated or their templates | 1,814 | 1,814 |

## What was dropped

| Change | Lines | PR |
|---|---|---|
| Page renderers no template uses, unused explorer charts, old harness-bias runner | -281 | #2 |
| Grok, Devin and Hetzner callers in the runners | -233 | #3 |
| Land-check acks for removals already on main (docs); `make grade` options added +2 code lines | -736 | #4 |
| Chart helpers, unread page and index code, contrast check copies | -69 | #5 |
| Phase-1 plan and report files (docs) | -124 | this change |

## What was kept, and why

- **`analysis/dataset.py`, 1,997 lines, unchanged.** Its code ran on nearly every line (1,670 of 1,684 traced on the first pass). It derives 736 facts, and the page and `make audit` depend on them.
- **`page.py`, `summarize.py`, `charts.py`, `grok.py`, about 3,050 lines.** Tracing the whole report and audit chain found about 100 unrun lines outside `landcheck.py`, mostly fallbacks for new data. So this code is live, not dead.
- **`CONFIGS`, flag lists, `key_for`, `cli_version`, the Claude budget guard.** Cache keys and `results/manifest.json` depend on them, including the retired lanes' entries.
- **`need()` tripwires, 187 call lines (171 in `dataset.py`).** They stop a sentence printing when the data no longer support it.
- **`docs/SETUP.md`, 208 lines.** Real documentation with facts found nowhere else; only one row changed.
- **`tools/check_colours.py`, 145 lines.** Only tests run it, but it guards the page's colours.

## Decided

- **Freeze dropped.** Copying closed sections into a data file would save about 450 lines net (an estimate; a prototype removed 196 from `_facts`). Those numbers would stop being derived, and `README.md` says its commands "rebuild committed data". That sentence would become partly false, and the README is locked.
- **Dedupe of `dataset.py`, `summarize.py` and `terra_priority.py` dropped.** It passed its checks but added 6 lines and saved about 800 bytes.
- **Grok, Devin and Hetzner callers removed.** No real run in the last 30 days, and no pending deviation in `PLAN.md`. The runner is at 7e946a6. Devin's refusal message was not exercised: the fake CLI failed earlier, in `cli_version`.
- **`make grade` now refuses to change existing rows.** It refuses today, because regrading the cache differs from all 1,261 rows in the function results. New configs use `python3 -m bench.grade_all --configs NAME --output results/NEW.jsonl`. The agentic and trim exports use the same writer.
- **Land-check acks cleared rather than kept.** They only match a base that still has those lines. Comparing against a base older than main would now report those removals again.
- **Docs target not forced.** See below.

## Left undone

**Code at 6,500 or below.** About 1,365 lines over. No refactor found this much without changing outputs. String literals with spaces are 19% to 24% of the bytes in the main generators (40% in `configs.py`), so the rest is mostly code that computes each number for its own sentence.

Output changes that would unlock lines. These are estimates, not built, and each needs the operator to accept a page change:

| Output change | Roughly |
|---|---|
| Remove the Grok comparison section | -600 (`grok.py` plus parts of `dataset.py`) |
| Remove closed appendix arms from the page: pilot, trim, quality, harness bias, Hetzner, Devin | -600 |
| Freeze those arms instead, and change the README sentence | -450 |
| Remove the explorer | -250 |

Together, the three removals could reach about 6,400, just under the phase-1 ceiling. **A few hundred lines is not reachable while this page stays**: it publishes 736 derived facts.

**Docs at 2,000 or below.** The lines the golden locks, or that must stay, come to about 2,074: `REPORT` 646, `page.tmpl` 527, `report.tmpl` 323, `PLAN` 152, `RAW_RUNS` 120, `README` 99, `readme.tmpl` 99, `audit_allow` 27, task and pilot markdown 81. That is above 2,000 before counting `SETUP.md`, this report or the plan. Hand-written docs alone are 643 lines.

**Stale text left in place.** `results/appendix/harness_bias.md` names the old runner command and is a recorded output. `results/README.md` still lists `analysis/harness_bias.py` for that appendix.

## Evidence

- `tools/gate.sh` on each landed stage: `pytest-exit=0`, `GOLDEN-CLEAN`, `BASELINE-SAME`.
- `make land-check BASE=origin/main`: 0 removals, 0 page findings on each.
- Generator differential, final code against the 7e946a6 generator, byte-identical across `dataset.json`, `page.html`, `tables.md`, `manifest.json`, `README.md`, `REPORT.md`, `RAW_RUNS.md` on six mutated inputs: none, new config, changed tokens, changed price, plus two with tripwires off (every open row's tokens and time changed; the same with one pass flipped in every config not already perfect). The harness is a scratch script and is not in this repo.
- Runner smoke with fake CLIs, on stage 2's code only: `bench.run` output matches baseline over 120 cached cells, `bench.agentic.run` matches apart from its output path. No later stage changed `bench/run.py` or `bench/agentic/run.py`. #4 changed `bench/grade_all.py`, exercised separately in a copy: `--configs haiku-low --output` wrote 146 rows, a repeat added none, and the default output refused.
- Live page: sha of `chimericlabs.xyz/dispatchbench/` equals `results/report/page.html` on main (ffe135b4d825).
- Reviews: Claude Opus 5.5 reviewed each PR; #4 was its own change, and on #5 it read part of the diff, and Claude Haiku reviewed all of `charts.py` and `page.py` after merge. Haiku found two differences no current data reach: a Devin config also in the main order no longer gets a duplicate grid column, and a config block missing `usd_per_pass` is dropped from the cost charts instead of raising. `summarize` always sets that key. Codex and Fable were unavailable per the brief, so no second-family review ran.
