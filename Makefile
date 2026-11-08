# make report needs no model CLI and makes no network calls: it rebuilds everything from cache/ and results/.
PY ?= python3
RUN_CONFIGS ?= haiku-low,haiku-medium,sonnet-medium,luna-low,luna-medium,sol61-medium
AGENT_CONFIGS ?= haiku-low,sonnet-medium,luna-low,sol61-medium
HARD_CONFIGS ?= sonnet-medium,sol61-medium,haiku-low,luna-high

.PHONY: land-check selftest run hard agentic grade report audit clean-report

land-check:          ## before landing: list page text and merge lines this branch removes; rerun with ACK=1 once each is intended
	$(PY) -m analysis.landcheck --base $${BASE:-main} $(if $(ACK),--ack)

selftest:            ## check every problem: reference == brute force, planted bugs fail, examples hold (about 12 min)
	$(PY) -m bench.selftest

run:                 ## function track (cached calls are skipped; costs money for new ones)
	$(PY) -m bench.run --phase main --configs $(RUN_CONFIGS) --problems all --repeats 1-5 --lanes 4

hard:                ## L7 rung, added after the main run (PLAN.md, deviation 16)
	$(PY) -m bench.run --phase hard --configs $(HARD_CONFIGS) --problems hard --repeats 1-5 --lanes 4

agentic:             ## agentic track (cached runs are skipped)
	$(PY) -m bench.agentic.run --configs $(AGENT_CONFIGS) --tasks all --repeats 1-3 --lanes 4

grade:               ## grade cached completions in the sandbox; refuses to rewrite existing results rows
	$(PY) -m bench.grade_all
	$(PY) -m bench.agentic.run --export
	$(PY) -m bench.arms export-trim

report:              ## render existing results; grading/export is explicit to preserve historical rows
	$(PY) -m analysis.summarize
	$(PY) -m analysis.dataset
	$(PY) -m analysis.charts
	$(PY) -m analysis.luna_rescue > results/report/luna_rescue.md
	$(PY) -m analysis.terra_priority > results/report/terra_priority.md
	$(PY) -m analysis.report
	$(PY) -m analysis.raw_runs
	$(PY) -m analysis.og

audit: contrast      ## fail if any committed number, table, chart, README or page differs from what the data give
	$(PY) -m analysis.audit

clean-report:
	rm -rf results/report results/manifest.json

# Read-only fetch from the site; SHA is deliberately required and immutable.
.PHONY: sync-design-system
sync-design-system:
	$(PY) docs/page/design-system/scripts/sync.py "$(SHA)" $(if $(SOURCE_REPO),--source-repo "$(SOURCE_REPO)")

.PHONY: contrast
contrast:            ## pinned site dark pairs and DispatchBench theme equivalents
	node docs/page/design-system/scripts/check-contrast.mjs
	$(PY) tools/check_contrast.py
