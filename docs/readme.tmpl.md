# model-routing-bench

Which model and reasoning effort should a coding task be routed to? This repo measures {{n_configs}} Claude Code and Codex CLI configs, plus {{n_new_codex}} Codex configs added on {{new_date}}, on {{n_all_problems}} Python problems written after the models' training cutoff, plus {{n_tasks}} small repo tasks.

## The answer

Claude and Codex are billed separately, so the table shows both: Claude $ is what the Claude side pays; list $ prices every call, Codex included, at list rates.

| Route to | When | Passed | Claude $ per pass | List $ per pass | Median s |
|---|---|---|---|---|---|
| **sol61-high**, haiku-low repairs only if a check fails | default while Codex has quota | {{sol61_high_k}} | {{claude_zero}} | {{sol61_high_upp}} | {{sol61_high_med}} |
| astra-medium, same repair | faster, about {{x_astra_vs_s61h}} the list price (Codex usage assumed to track it) | {{astra_medium_k}} | {{claude_zero}} | {{astra_medium_upp}} | {{astra_medium_med}} |
| haiku-low | Codex out | {{haiku_low_k}} | {{haiku_low_upp}} | {{haiku_low_upp}} | {{haiku_low_med}} |
| haiku-medium | Codex out and a miss is costly | {{haiku_medium_k}} | {{haiku_medium_upp}} | {{haiku_medium_upp}} | {{haiku_medium_med}} |

Main ladder: {{n_problems}} problems × {{repeats}} attempts per config.

- **Trust first, then save.** A cheap model plus a Haiku reviewer costs more than haiku-medium alone, because Haiku redoes the work. Savings come only from a builder that is right on its own.
- **sol61-high and astra-medium never failed**: every main-ladder attempt, every attempt on the hardest rung, and all {{ag_n}} repo-task runs. With the Haiku repair gated on the statement's examples, they needed {{g_sol61_repairs}} and {{g_astra_repairs}} repairs on luna's hardest problems ({{r_sol61_high_haiku_on_fail_k}} and {{r_astra_medium_haiku_on_fail_k}}).
- **The price is time.** On the repo tasks they take {{ag_sol61_high_med}} s and {{ag_astra_medium_med}} s at the median, against about {{ag_claude_med}} s for haiku-low and sonnet-medium.
- **Skip luna at low or medium effort.** It barely reasons there and misses easy problems. luna-high is the cheapest Codex config but misses some.
- **sonnet-medium also never failed** ({{sm_all}}); it is the cheapest of the three by list price.

Total spend: {{claude_usd}} Claude, {{codex_usd}} Codex at list prices ({{codex_new_usd}} of it for the Codex models added on {{new_date}}, {{fm_usd}} for the fast-mode and xhigh runs).

## Read more

- **[Interactive report](results/report/page.html)**: charts and sortable tables in one self-contained HTML file. Download it and open it in a browser.
- **[Full report](docs/REPORT.md)**: method, every table, the appendices, limitations.
- **[Every model answer](results/solutions/README.md)**: per problem, with a short note on the problem and the correct approach, so you can judge the code.
- **[Pre-registration](PLAN.md)**: what was planned before any model call, and each deviation.
- Raw data: `results/*.jsonl`; prices: [results/prices.json](results/prices.json).

## For agents

- `README.md`, `docs/REPORT.md` and `results/report/page.html` are generated. Edit `docs/readme.tmpl.md`, `docs/report.tmpl.md` or `docs/page.tmpl.md`, then run `make report && make audit`.
- Every number in a template is a fact computed in `analysis/report.py`. A bare number fails `make audit` unless `docs/audit_allow.json` lists it.
- `make report` makes no model calls. New runs go through `bench/run.py` (cache-first, with a Claude spend cap).
- Repo layout: the Layout section of [docs/REPORT.md](docs/REPORT.md).

MIT licence, see [LICENSE](LICENSE).
