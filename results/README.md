# results/ index

Path | what | produced by | read by. Cache (`cache/`, 15 MB) holds raw call transcripts and is not indexed per file.

## Raw run rows (jsonl)
- `2026-10-22b-function.jsonl` function track, all configs, phases main/exploratory/escalation/fastmode/hard/calibration | bench runner | summarize, dataset
- `2026-10-22b-agentic.jsonl` repo tasks | bench runner | summarize, dataset
- `2026-10-25-isolated-agentic.jsonl` clean-home rerun of the repo tasks (the headline repo-task rows; patches in `cache/isolated/agentic_patches/`) | bench runner | summarize, dataset
- `2026-10-26-grok-function.jsonl`, `2026-10-28-grok-spectrum-function.jsonl` Grok function track (first run, then the full spectrum) | bench runner | summarize, dataset, grok
- `2026-10-27-grok-agentic.jsonl` Grok repo tasks (patches in `cache/agentic_patches/`) | bench runner | dataset, grok
- `2026-10-28-terra-function.jsonl` gpt-5.6-terra function track | bench runner | summarize, dataset
- `2026-10-28-devin-function.jsonl` Devin function track (one repeat, free tier, no dollars) | devin runner | summarize, dataset
- `2026-10-22b-trim.jsonl` Codex harness trim probe | bench.trim_probe | summarize, dataset
- `2026-10-22-pilot.jsonl`, `2026-10-22-pilot-agentic.jsonl` early pilot | bench runner | dataset, report appendix
- `quality.jsonl`, `quality_meta.json` readability grades | quality step | report.quality_table
- `agentic_tests.json` hidden repo-task tests | agentic export | agentic grader

## Prices and summaries
- `prices.json` list prices and fast-mode multiplier | hand-kept | summarize, dataset
- `dataset.json` the one file every renderer reads: rows (config x set, with the pass rule), facts, tables, design, annotations, generated_from (jsonl + sha256) | analysis.dataset (`make report`) | charts, report, page, grok, raw_runs, audit
- `manifest.json` run provenance | summarize | audit

## Appendix experiments
- `appendix/luna_rescue.jsonl` rescue pipeline arms on 7 hard problems | bench rescue | luna_rescue, dataset
- `appendix/blind_readability.json` | blind grading | report
- `appendix/harness_bias.jsonl`, `codex_harness.jsonl` harness-bias runs | bench harness-bias runner | analysis.harness_bias, dataset

## Generated report (do not edit)
- `report/page.html`, `report/charts/*.svg` (9), `report/tables.md`, `report/luna_rescue.md` | analysis.report, charts, luna_rescue | readers, audit

## Research and reviews
- `solutions/` model answers kept for grading | bench | graders
- `research/review-sol61/REVIEW.md` independent review of the bench and page (branch review-sol61) | a reviewer session | humans; findings tracked in the page work
- `research/review-astra/REVIEW.md` second review (branch review-astra); both were root REVIEW.md files, moved here to avoid the name clash | a reviewer session | humans
- `review-sol61/probe.py`, `probe.json`, `audit.txt` offline fairness and harness probes and their output | probe.py (offline, no model calls) | REVIEW.md, receipt.json
- `review-sol61/receipt.json` historical hashes of the reviewed files | the reviewer | nobody at run time; receipt.json still names the old root path REVIEW.md and the removed bundle
- `review-sol61/review.bundle` was removed from the tree on 2026-10-28 because it contains a local home path and needs a parent commit outside public history, so it cannot be imported. Older commits still contain it; read `research/review-sol61/REVIEW.md` instead.
- `review-astra/probe.json` output of `bench/review_probe.py` | bench/review_probe.py | research/review-astra/REVIEW.md
- `codex-own-harness` is merged (via fairness-qa): `appendix/harness_bias.jsonl`, `appendix/codex_harness.jsonl` | analysis/harness_bias.py | dataset, page Q&A

## Proposed moves (none made)
- `quality*.json*` and `agentic_tests.json` into `results/inputs/`; `prices.json` stays.
- `appendix/*` stays; reviews already live in `results/research/<branch>/`.
Each move needs its readers rewritten, then `make report`, `python3 -m analysis.audit`, `python3 -m pytest -q tests`.

summary.json is gone: the summary is computed in memory and folded into dataset.json. Add a config to `analysis/configs.py` when a new run lands; audit enforces it.
