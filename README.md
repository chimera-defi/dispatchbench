# model-routing-bench

Which model and reasoning effort should a coding task be routed to? This repo measures 6 Claude Code and Codex CLI configs on 15 Python problems written after the models' training cutoff, plus 4 small repo tasks.

## The answer

| Route to | Passed | $ per pass | Median s |
|---|---|---|---|
| **haiku-medium** (default) | 59/60 | $0.00149 | 13.0 |
| haiku-low (tight budget) | 57/60 | $0.00112 | 10.0 |
| luna-high (cheapest Codex) | 55/60 | $0.00105 | 12.2 |
| sol61-medium | 58/60 | $0.01499 | 22.6 |

Main ladder: 12 problems × 5 attempts per config.

- **Skip luna at low or medium effort.** It barely reasons there and misses easy problems.
- **On luna's hardest problems** haiku-medium never missed (35/35, $0.00192 per pass). luna-high with Haiku repairing only failed checks is cheaper ($0.00135) but passes 32/35.
- **sonnet-medium never failed** (75/75) at about 8× haiku-medium's price.

Total spend: $2.06 Claude, $2.42 Codex at list prices.

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
