# DispatchBench

Which model should a coding task go to?

[Live report](https://chimericlabs.xyz/dispatchbench/) · [Interactive report](results/report/page.html) · [Full report](docs/REPORT.md) · [Answers](results/solutions/README.md)

## What it measures

We compare {{n_ladder_configs}} model-and-effort configs on fresh Python problems.
The main run used {{n_configs}} of them on {{n_problems}} problems.
The set contains {{n_all_problems}} problems and {{n_tasks}} small repository tasks.
Function tasks ask for one answer, with no tool use allowed.
Repository tasks use agent CLIs, with code execution and retries.

## The answer

| Route to | When | Main ladder passed | List $ per pass | Median seconds |
|---|---|---|---|---|
| sol61-high ⚡ | Default with Codex quota | {{ff_s61_k}} | ~{{ff_s61_upp}} | {{ff_s61_med}} |
| haiku-high | Cheapest config without misses | {{hh_k}} | {{hh_upp}} | {{hh_med}} |
| sonnet-medium | Speed first | {{sonnet_medium_k}} | {{sonnet_medium_upp}} | {{sonnet_medium_med}} |

Main ladder: {{n_problems}} problems, each attempted {{repeats}} times per config.

Total spend: {{claude_usd}} Claude, about {{codex_usd_rounded}} Codex (estimated).

## How to read it

Pass rate measures answers passing every hidden test.
Read each problem set separately.
Claude dollars use CLI-reported costs.
Codex dollars estimate tokens at list prices; subscriptions use quota.
⚡ marks fast mode at the same model and effort.
Problem labels show number, name, and rung.

The [interactive report](results/report/page.html) contains every config, uncertainty intervals, findings, and method.
The [full report](docs/REPORT.md) explains pipelines, additional experiments, and grading.
[PLAN.md](PLAN.md) records the original plan and deviations.

## Reproduce

These commands rebuild committed data, without model calls or model credentials.

```bash
git clone https://github.com/chimera-defi/dispatchbench.git
cd dispatchbench
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m analysis.dataset
python3 -m analysis.charts
python3 -m analysis.report
python3 -m analysis.audit
python3 -m pytest -q tests
python3 -m analysis.landcheck --base HEAD
```

## Data layout

| Path | Contents |
|---|---|
| `bench/problems/` | Problem statements, references, and planted bugs |
| `bench/agentic/` | Repository tasks, tests, and runner |
| `cache/` | Cached calls, completions, and verdicts |
| `results/*.jsonl` | Graded rows |
| `results/*isolated*` | Selected clean-home repository reruns |
| `results/agentic_tests.json` | Retained transcript metrics |
| `results/prices.json` | Pricing inputs |
| `results/dataset.json` | Computed facts and tables |
| `results/manifest.json` | Input provenance |
| `analysis/` | Offline analysis, charts, rendering, and audits |
| `docs/*.tmpl.md` | Editable report templates |
| `results/report/` | Generated charts and interactive page |

## Publishing

The live page is chimericlabs.xyz/dispatchbench/.
The site downloads `results/report/page.html` from `main` at each deploy.
It also redeploys daily, so a push to `main` goes live within a day.
To publish at once, run the site's deploy workflow:

```bash
gh workflow run pages.yml -R chimera-defi/chimericlabs-llc
```

## License

MIT; see [LICENSE](LICENSE).

## Cite

{{cite}}
Machine-readable metadata: [CITATION.cff](CITATION.cff).
