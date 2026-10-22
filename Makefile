# make report needs no model CLI and makes no network calls: it rebuilds everything from cache/ and results/.
PY ?= python3
RUN_CONFIGS ?= haiku-low,haiku-medium,sonnet-medium,luna-low,luna-medium,sol61-medium
AGENT_CONFIGS ?= haiku-low,sonnet-medium,luna-low,sol61-medium
HARD_CONFIGS ?= sonnet-medium,sol61-medium,haiku-low,luna-high

.PHONY: selftest run hard agentic grade report clean-report

selftest:            ## check every problem: reference == brute force, planted bugs fail, examples hold (about 12 min)
	$(PY) -m bench.selftest

run:                 ## function track (cached calls are skipped; costs money for new ones)
	$(PY) -m bench.run --phase main --configs $(RUN_CONFIGS) --problems all --repeats 1-5 --lanes 4

hard:                ## L7 rung, added after the main run (PLAN.md, deviation 16)
	$(PY) -m bench.run --phase hard --configs $(HARD_CONFIGS) --problems hard --repeats 1-5 --lanes 4

agentic:             ## agentic track (cached runs are skipped)
	$(PY) -m bench.agentic.run --configs $(AGENT_CONFIGS) --tasks all --repeats 1-3 --lanes 4

grade:               ## grade cached completions in the sandbox, write results/*.jsonl
	$(PY) -m bench.grade_all
	$(PY) -m bench.agentic.run --export
	$(PY) -m bench.trim_probe --step export

report: grade        ## summary.json, manifest.json, tables.md, charts
	$(PY) -m analysis.summarize
	$(PY) -m analysis.charts
	$(PY) -m analysis.luna_rescue > results/report/luna_rescue.md

clean-report:
	rm -rf results/report results/summary.json results/manifest.json
