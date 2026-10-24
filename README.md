# model-routing-bench

Which model and reasoning effort should a coding task be routed to? This repo measures 6 Claude Code and Codex CLI configs, plus 5 Codex configs added on 2026-10-23, on 15 Python problems written after the models' training cutoff, plus 4 small repo tasks.

## The answer

Claude and Codex are billed separately, so the table shows both: Claude $ is Claude CLI-reported cost (list basis); Codex $ is a token-price estimate. The list $ column combines those two accounting bases.

| Route to | When | Passed | Claude $ per pass | List $ per pass | Median s |
|---|---|---|---|---|---|
| **sol61-high**, haiku-low repairs only if a check fails | default while Codex has quota | 60/60 | $0 | $0.0186 | 27.4 |
| astra-medium, same repair | faster, about 4.0× the list price (Codex usage assumed to track it) | 60/60 | $0 | $0.0753 | 20.9 |
| haiku-low | Codex out | 57/60 | $0.001122 | $0.001122 | 10.0 |
| haiku-high | Codex out and a miss is costly (exploratory) | 60/60 | $0.002822 | $0.002822 | 14.7 |

Main ladder: 12 problems × 5 attempts per config.

- **Trust first, then save.** A cheap model plus a Haiku reviewer costs more than haiku-medium alone, because Haiku redoes the work. Savings come only from a builder that is right on its own.
- **sol61-high and astra-medium never failed**: every main-ladder attempt, every attempt on the hardest rung, and all 12 repo-task runs. With the Haiku repair gated on the statement's examples, they needed 0 and 0 repairs on luna's hardest problems (35/35 and 35/35).
- **The price is time.** On the repo tasks they take 109 s and 85 s at the median, against about 28 s for haiku-low and sonnet-medium.
- **Skip luna at low or medium effort.** It barely reasons there and misses easy problems. luna-high is the cheapest Codex config but misses some.
- **Fast mode (⚡) keeps the passes and costs about twice as much per pass.** sol61-high ⚡: 60/60, 17.4 s against 27.4 s; astra-medium ⚡: 60/60, 9.9 s against 20.9 s. Neither missed on L7 (15/15, 15/15).
- **haiku-high and sonnet-medium also never failed.** haiku-high: 60/60, 15/15 on L7 and 12/12 repo tasks at $0.002822 per pass, 7× cheaper than sol61-high and faster (14.7 s against 27.4 s). haiku-medium still misses (13/15 on L7). sonnet-medium: 75/75, the fastest of them.

Function + agentic spend only (auxiliary runs and pilot excluded): $2.46 Claude, $35.40 Codex at list prices ($16.70 of it for the Codex models added on 2026-10-23, $3.41 for the fast-mode and xhigh runs).

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
