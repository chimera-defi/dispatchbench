# model-routing-bench

Which model and reasoning effort should a coding task be routed to? This repo measures {{n_configs}} Claude Code and Codex CLI configs on {{n_all_problems}} Python problems written after the models' training cutoff, plus {{n_tasks}} small repo tasks.

## The answer

| Route to | Passed | $ per pass | Median s |
|---|---|---|---|
| **haiku-medium** (default) | {{haiku_medium_k}} | {{haiku_medium_upp}} | {{haiku_medium_med}} |
| haiku-low (tight budget) | {{haiku_low_k}} | {{haiku_low_upp}} | {{haiku_low_med}} |
| luna-high (cheapest Codex) | {{luna_high_k}} | {{luna_high_upp}} | {{luna_high_med}} |
| sol61-medium | {{sol61_medium_k}} | {{sol61_medium_upp}} | {{sol61_medium_med}} |

Main ladder: {{n_problems}} problems × {{repeats}} attempts per config.

- **Skip luna at low or medium effort.** It barely reasons there and misses easy problems.
- **On luna's hardest problems** haiku-medium never missed ({{r_haiku_medium_k}}, {{r_haiku_medium_upp}} per pass). Stripped-harness luna-high with Haiku repairing only failed checks is cheaper ({{r_luna_high_bare_haiku_on_fail_upp}}) but passes {{r_luna_high_bare_haiku_on_fail_k}}.
- **Other Codex models don't change this.** gpt-5.6-sol (high) and gpt-6-astra (medium) pass {{x_sol56_high_k}} and {{x_astra_medium_k}}, at {{x_sol56_vs_hm}} and {{x_astra_vs_hm}} haiku-medium's price per pass. gpt-5.6-luna is worse and dearer than gpt-6 luna.
- **sonnet-medium never failed** ({{sm_all}}) at about {{sm_vs_hm_x}} haiku-medium's price.

Total spend: {{claude_usd}} Claude, {{codex_usd}} Codex at list prices ({{codex_new_usd}} of it for the Codex models added on {{new_date}}).

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
