# results/ index

Path | what | produced by | read by. Cache (`cache/`, 15 MB) holds raw call transcripts and is not indexed per file.

## Raw run rows (jsonl)
- `2026-10-22b-function.jsonl` function track, all configs, phases main/exploratory/escalation/fastmode/hard/calibration | bench runner | summarize, dataset
- `2026-10-22b-agentic.jsonl` repo tasks | bench runner | summarize, dataset
- `2026-10-22b-trim.jsonl` Codex harness trim probe | bench.trim_probe | summarize, dataset
- `2026-10-22-pilot.jsonl`, `2026-10-22-pilot-agentic.jsonl` early pilot | bench runner | dataset, report appendix
- `quality.jsonl`, `quality_meta.json` readability grades | quality step | report.quality_table
- `agentic_tests.json` hidden repo-task tests | agentic export | agentic grader

## Prices and summaries
- `prices.json` list prices and fast-mode multiplier | hand-kept | summarize, dataset
- `summary.json` metrics per config | analysis.summarize | charts, report, page, audit
- `dataset.json` one row per config x set (and an all-runs roll-up) | analysis.dataset (`make report`) | charts (migrated ones), "Everything we tried", audit
- `manifest.json` run provenance | summarize | audit

## Appendix experiments
- `appendix/luna_rescue.jsonl` rescue pipeline arms on 7 hard problems | bench rescue | luna_rescue, dataset
- `appendix/blind_readability.json` | blind grading | report
- `appendix/harness_bias.jsonl`, `codex_harness.jsonl` arrive with branch codex-own-harness | registry already lists them

## Generated report (do not edit)
- `report/page.html`, `report/charts/*.svg` (9), `report/tables.md`, `report/luna_rescue.md` | analysis.report, charts, luna_rescue | readers, audit

## Research and reviews
- `solutions/` model answers kept for grading | bench | graders
- Branches to merge (not merged here): review-astra, review-sol61, codex-own-harness. Their REVIEW.md files conflict by name; land each under
  `results/research/<branch>/`.

## Proposed moves (none made)
- `quality*.json*` and `agentic_tests.json` into `results/inputs/`; `prices.json` stays.
- `appendix/*` stays; reviews go to `results/research/<branch>/`.
Each move needs its readers rewritten, then `make report`, `python3 -m analysis.audit`, `python3 -m pytest -q tests`.

summary.json is unchanged in this pass. Add a config to `analysis/configs.py` when a new run lands; audit enforces it.
