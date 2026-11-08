# SHRINK-REPORT: dispatchbench harness (2026-11-08)

Plan: [SHRINK-PLAN.md](SHRINK-PLAN.md). The Claude advisor tool reviewed the plan and the work transcript (it did not read the diff line by line); builders were Sonnet 5.5. Codex out, Fable paused, no Grok.

## Result: phase 1 landed, phase 2 not done
| non-data lines | before (b9fc17b) | after | change |
|---|---|---|---|
| code (bench, analysis, tools, Makefile) | 11,601 | 8,446 | -27% |
| tests | 5,337 (294 tests, 5 min) | 884 (48 tests, 5 min) | -83% |
| docs (md) | 3,142 | 3,107 | -1% (links to deleted files got longer `blob/b9fc17b/` URLs) |
| page source (html/js/css) | 1,174 | 1,174 | unchanged by design |
| problems and repo tasks (benchmark inputs) | 3,964 | 3,571 | the 393-line drop is deleted pilot code (`bench.py`, `checker.py`, `summarize.py`, `e2e.py`) that the counter filed under data; counted as dropped code |
| recorded data `results/`, `cache/` | 464k lines | untouched |

The budget in the plan was code ≤ 6,500 and docs ≤ 2,000. **Both missed.** The remaining code is the report generator (`dataset.py` 1,997, `page.py` 1,339, `charts.py` 715, `summarize.py` 685, `grok.py` 495) plus the runner (`run.py` 495, `agentic/run.py` 271): it produces a 100 KB page that must stay byte-identical, and shrinking it without changing a byte was not reached.

## Proof it still works (final `tools/gate.sh`)
`tools/gate.sh` at the final commit: `make report` ok, `make audit` ok (21 generated files compared), `pytest-exit=0` (48 passed, 228 s), `GOLDEN-CLEAN` (git diff empty, no untracked files). Baseline at b9fc17b was the same gate: 294 passed, GOLDEN-CLEAN. Phase A's gate was GOLDEN-DIRTY only for the intentional doc-link, Makefile and dataset.json `pin` edits, which were then committed and re-gated clean.

## Contract proof against the baseline tag (not HEAD)
- `git diff pre-shrink HEAD -- results/report README.md docs/REPORT.md`: no diff in `results/report/` or `README.md`; `docs/REPORT.md` loses only the five layout-tree lines for deleted files.
- `results/dataset.json`: only the `pin` of the `esc_max` entry is removed (it pointed at deleted `bench/escalate.py`); its `source` text is unchanged.
- `results/report/page.html` sha256 `ffe135b4...63b9` is identical at `pre-shrink`, at HEAD and on live `raw.githubusercontent.com/.../main` (curl, 11-08), and the live copy contains `<title>DispatchBench`. There are no deployed copies of the harness; page.html is the only deployed artifact, so nothing needs a deploy diff.
- `analysis.landcheck --base main`: 0 removals, 0 page-integrity findings. gitleaks over the branch: no leaks.

## Dropped, and why
- One-off appendix runners with no calls after 10-28 (results stay): `escalate`, `trim_probe` (runner), `plan_first`, `gated_repair` (runner), `review_probe`, `regrade_t1`, `isolated`, `quality/`, `pilot/` code, `codex_harness`.
- Generators with no calls: `export_solutions`, `problem_notes`, `agentic_tests`. Committed outputs (`results/solutions/`, `agentic_tests.json`) stay.
- Provider fixture tests (hetzner, devin, grok), 246 tests that duplicated `make audit` or pinned prose, `docs/MIGRATION.md`, unreferenced `docs/TERRA_PRIORITY.md`.
- Makefile targets: `escalate`, `trim`, `plan-first`, `gated-repair`, `solutions`, `quality`.
- Old code stays at git tag `pre-shrink` (b9fc17b, local) and on origin at that commit; deleted-file links point at `blob/b9fc17b/...`.

## Kept, and why
`make report|audit|land-check|run|hard|agentic|grade|selftest|contrast` (30-day calls: 197, 181, 86, 16, 4 ...). `bench/grade.py`, `sandbox_exec.py`, `pilot/min_instructions.txt` (hash-pinned cache-key inputs). `bench/arms.py` (new, ~150 lines): names the report and runner still import from the deleted `trim_probe`/`gated_repair`, and `python3 -m bench.arms export-trim` replaces `trim_probe --step export` in `make grade`. README "Reproduce" argv unchanged. PLAN.md (cited preregistration). Test guards: fonts, self-contained page, deep links, visible charts/xfig, sorting, Grok bytes, single source, colours, grader invariants, plus the four Chrome runtime checks. 15 of the guards were mutation-checked by the builder; unchecked: cost-kind runtime, any-pair projection, manifest independence, `@font-face`, grader tests.

## External contracts and the cited ruling
- Site deploy fetches `raw.githubusercontent.com/chimera-defi/dispatchbench/main/results/report/page.html` and greps `<title>DispatchBench`. `results/report/page.html` is byte-identical after this change, so the deploy is unaffected (live check below).
- Host staffing rulings cite `dispatchbench f77c040`. That commit is **not an ancestor of main** (rewritten history; only on local `dbench/*` branches). Its Terra result files are on main: four identical, three supersets (+90, +40, +15 rows). Local tags `pre-shrink` and `ruling/f77c040` keep the commits reachable on this host; not pushed on purpose.

## Decided
1. Superseded `shrink-1101` instead of merging: older base (76de74d), 45 harness files differ from main, and it shrinks page content the operator's regression reports require. Left untouched.
2. Page stays byte-identical; shrink code under it. Phase 2 (generator rewrite) split off.
3. No CI exists in the repo, so "green CI" = `tools/gate.sh` (report, audit, pytest, clean tree) + landcheck + Claude review; merged with a merge commit, no history rewrite.
4. `bench.selftest` and `make selftest` kept (4 calls, cheap, validates the problems).
5. `land-check` default base changed from stale `fast-mode-main` to `main`.
6. Tags not pushed (f77c040 is rewritten-away history).
7. Test target 1,200 lines became 884; guards chosen by regression reports, not coverage.

## Left undone
- Phase 2: rewrite or slim `dataset.py`/`page.py`/`charts.py`/`summarize.py`/`grok.py` (about 5.2k lines) under the byte-identical golden.
- Runner smoke: `/bin/false` CLIs miss the cache (cache keys include `cli_version`; cached rows are 2.1.308). With fake CLIs reporting 2.1.308: `bench.run` 120/120 cached; `bench.agentic.run` 66/72 (the 6 misses are `t1_discount`: cache has no entry under the current t1 hidden-suite grader version); `bench.grade_all` rewrote two `results/2026-10-22b-*.jsonl` files (restored). **Run on the baseline tag too, with identical results** (`bench.run` 120/120, `agentic.run` t1_discount ERR 0/0, `grade_all` rewrote both files): pre-existing, not caused by the shrink. `make grade` still rewrites historical 10-22b rows from the cache and must not be run on main without a diff review; fixing it is undone.
- Stale text in generated output kept to hold bytes: `results/solutions/README.md` mentions deleted `export_solutions`/`pilot/checker.py`; `docs/page.tmpl.md:271` names `bench/codex_harness.py`; `report.tmpl.md:142` says `make quality`; `bench/pilot/README.md` remains.
- `make audit` was assumed, not verified, to cover the dropped median, fairness and landcheck tests; `analysis.landcheck` (86 calls) now has no test and was checked only by running it live.
- Dropped weaker guards: phone/desktop label-clearance and badge tests, explorer config-hash deep-link JS test, `@font-face` check (Google Fonts link checked instead).
- 30-day usage evidence is agent transcripts only; shell history has no dispatchbench entries and no cron, timer or hook touches the bench.

## Archive candidates
Sibling local checkouts (about 20 `dispatchbench-*`) were surveyed and not touched; the per-checkout state table (branch, unpushed commits, dirty files) is in the host-side copy of this report.
