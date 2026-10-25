# DispatchBench

LeetCode-style problems, written fresh for this bench.

**[Interactive report](results/report/page.html)** · [Full report](docs/REPORT.md) · [Raw data](results/) · [Reproduce](#reproduce) · [Cite](#cite)

![Pass rate against $ per passing solution on the main ladder; up and left is better](results/report/charts/hero.svg)

Which model and reasoning effort should a coding task be routed to? This repo measures {{n_configs}} Claude Code and Codex CLI configs, plus {{n_new_codex}} Codex configs added on {{new_date}}, on {{n_all_problems}} Python problems written after the models' training cutoff, plus {{n_tasks}} small repo tasks.

## The answer

Claude and Codex are billed separately, so the table shows both: Claude $ is Claude CLI-reported cost (list basis); Codex $ is a token-price estimate. The list $ column combines those two accounting bases.

| Route to | When | Passed | Claude $ per pass | List $ per pass | Median s |
|---|---|---|---|---|---|
| **sol61-high**, haiku-low repairs only if a check fails | default while Codex has quota | {{sol61_high_k}} | {{claude_zero}} | {{sol61_high_upp}} | {{sol61_high_med}} |
| astra-medium, same repair | faster, about {{x_astra_vs_s61h}} the list price (Codex usage assumed to track it) | {{astra_medium_k}} | {{claude_zero}} | {{astra_medium_upp}} | {{astra_medium_med}} |
| haiku-low | Codex out | {{haiku_low_k}} | {{haiku_low_upp}} | {{haiku_low_upp}} | {{haiku_low_med}} |
| haiku-high | Codex out and a miss is costly (exploratory) | {{hh_k}} | {{hh_upp}} | {{hh_upp}} | {{hh_med}} |

Main ladder: {{n_problems}} problems × {{repeats}} attempts per config.

- **Trust first, then save.** A cheap model plus a Haiku reviewer costs more than haiku-medium alone, because Haiku redoes the work. Savings come only from a builder that is right on its own.
- **sol61-high and astra-medium never failed**: every main-ladder attempt, every attempt on the hardest rung, and all {{ag_n}} repo-task runs. With the Haiku repair gated on the statement's examples, they needed {{g_sol61_repairs}} and {{g_astra_repairs}} repairs on luna's hardest problems ({{r_sol61_high_haiku_on_fail_k}} and {{r_astra_medium_haiku_on_fail_k}}).
- **The price is time.** On the repo tasks they take {{ag_sol61_high_med}} s and {{ag_astra_medium_med}} s at the median, against about {{ag_claude_med}} s for haiku-low and sonnet-medium.
- **Skip luna at low or medium effort.** It barely reasons there and misses easy problems. luna-high is the cheapest Codex config but misses some.
- **Fast mode (⚡) keeps the passes and costs about twice as much per pass.** sol61-high ⚡: {{ff_s61_k}}, {{ff_s61_med}} s against {{ff_s61_dmed}} s; astra-medium ⚡: {{ff_ast_k}}, {{ff_ast_med}} s against {{ff_ast_dmed}} s. Neither missed on L7 ({{ff_s61_hk}}, {{ff_ast_hk}}).
- **haiku-high and sonnet-medium also never failed.** haiku-high: {{hh_k}}, {{hh_hk}} on L7 and {{ag_hh_k}} repo tasks at {{hh_upp}} per pass, {{hh_s61h_x}} cheaper than sol61-high and faster ({{hh_med}} s against {{sol61_high_med}} s). haiku-medium still misses ({{hm_l7_k}} on L7). sonnet-medium: {{sm_all}}, the fastest of them.

Function + agentic spend only (auxiliary runs and pilot excluded): {{claude_usd}} Claude, {{codex_usd}} Codex at list prices ({{codex_new_usd}} of it for the Codex models added on {{new_date}}, {{fm_usd}} for the fast-mode and xhigh runs).

## Read more

- **[Interactive report](results/report/page.html)**: charts and sortable tables in one self-contained HTML file. Download it and open it in a browser.
- **[Full report](docs/REPORT.md)**: method, every table, the appendices, limitations.
- **[Every model answer](results/solutions/README.md)**: per problem, with a short note on the problem and the correct approach, so you can judge the code.
- **[Pre-registration](PLAN.md)**: what was planned before any model call, and each deviation.
- Raw data: `results/*.jsonl`; prices: [results/prices.json](results/prices.json).

## Reproduce

```bash
git clone https://github.com/chimera-defi/dispatchbench.git && cd dispatchbench
make report && make audit
```

This rebuilds every table, chart and page from the committed cache. It makes no model calls. Needs Python and make; `pip install -r requirements.txt` adds pytest for `python3 -m pytest tests`.

## Add a model

1. Add a line to `CONFIGS` in `bench/run.py`: name → (CLI, model id, effort).
2. Register it with `add(...)` in `analysis/configs.py`. A Codex model also needs its price in `results/prices.json`.
3. Run `python3 -m bench.run --phase exploratory --configs <name>`. This makes real model calls and spends money.
4. Run `make grade && make report && make audit`. The audit names anything left to wire up.

The grader runs model-written code with CPU and memory limits only, not network or file isolation. Grade new code in a container or VM.

## For agents

- `README.md`, `docs/REPORT.md` and `results/report/page.html` are generated. Edit `docs/readme.tmpl.md`, `docs/report.tmpl.md` or `docs/page.tmpl.md`, then run `make report && make audit`.
- Every number in a template is a fact computed in `analysis/report.py`. A bare number fails `make audit` unless `docs/audit_allow.json` lists it.
- `make report` makes no model calls. New runs go through `bench/run.py` (cache-first, with a Claude spend cap).
- Repo layout: the Layout section of [docs/REPORT.md](docs/REPORT.md).

## Cite

{{cite}} Metadata: [CITATION.cff](CITATION.cff).

MIT licence, see [LICENSE](LICENSE).
