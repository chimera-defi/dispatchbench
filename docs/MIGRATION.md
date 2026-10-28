# Moving charts and tables onto the dataset

One source of truth: `results/*.jsonl` -> `analysis/dataset.py` -> `results/dataset.json` (one row per config x set, written by `make report`) plus
`analysis/configs.py` (the registry: name, category, description, source file). Charts and tables read only those two.

## Rules
1. Every dataset row carries `set` (main ladder, partial ladder, extra repeats, L7 set, calibration, repo tasks, rescue arms, pilot, pilot repo task,
   trim probe, harness bias, and "all runs" = the roll-up). Sets are exclusive; `dataset.build()` puts each result row in exactly one.
2. A chart helper takes a `set_` argument (see `charts.ladder(ds, s, set_="main ladder")`). A chart must not mix sets unless it shows a set selector or a
   label. Example to fix: the charts-repairs-toggle branch plots rescue arms (35 hard problems) beside main-ladder configs (60 calls); luna-low is 46/60 on
   one and 21/35 on the other.
3. Dollars are formatted by `dataset.usd()` only (one precision ladder: $x.xx from $1, 4 decimals from $0.01, 6 below, "$0", dash for None).
   The old charts keep their own formats until they migrate, to stay byte-identical.
4. Metrics are not recomputed in a chart. If a number is missing, add a column in `dataset._row` (which reuses `summarize.cost`, `stats.hier_boot`).
5. A new config goes in `configs.py`; `python3 -m analysis.audit` fails on a config with rows but no entry, an entry with no rows, a stale
   `results/dataset.json`, or a registered config missing from the page's "Everything we tried" section.

## Before / after (cost_total.svg, cost_per_1k.svg, token_in.svg are migrated; output is byte-identical)
Before: `for c, v, x in all_configs(s): ... v["usd_total"], v["tokens_mean"]["in_tok"]` (summary.json, rounded and reshaped).
After:
```python
rows = ladder(ds or dataset.read(), s)                      # [(config, dataset row, hollow)] for the main-ladder set
tot = [(r["display"], r["spend"], FAMILY(c), x) for c, r, x in rows]
```
Pattern for the rest: add `ds=None` to the signature, `build(s, ds)` passes it, pick rows with the set, read columns, never open a jsonl.
Acceptance for each chart: `make report` leaves `git diff --stat results/report/charts` empty (or the diff is an intended fix), audit OK, tests pass.

## Remaining functions and what they read today
| function | reads |
|---|---|
| charts.pareto_chart, cost_time_chart, rung_chart, heatmap, floor_chart | summary.json (`configs`, `exploratory`, by_rung, by_problem, token floor) |
| charts.agentic_chart | summary.json `agentic` (hidden_pass_rate, ci95, usd_per_run, by_task); dataset has the repo-tasks set, but not by_task yet |
| report.facts, tables_md, quality_table, fastmode_tables | summary.json plus results/quality.jsonl and prices.json |
| page.short_table, page.widgets | summary.json |
| luna_rescue.arms/table | appendix/luna_rescue.jsonl plus main rows (baseline arms) |
| fast_gate | summary.json fast-mode block |
| configs.section ("Everything we tried") | dataset.json, all-runs rows |

## Known gaps
- Rescue-problem baselines (main-run configs on the 7 rescue problems, for example luna-low 21/35) are not dataset rows yet; they need a "rescue problems" slice
  of the main rows, which would overlap the main ladder set, so the set model needs a second axis (problem subset) before the rescue chart migrates.
- by_task / by_problem / by_rung breakdowns are not columns yet.
- The audit rule "every number shown equals the dataset" is checked for the Everything table (pass counts) and the migrated charts (byte equality); the
  other numbers come from the same dataset.json (its `report` block), folded in from `summarize` in memory; summary.json no longer exists.
