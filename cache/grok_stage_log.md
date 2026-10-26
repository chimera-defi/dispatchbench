# Grok staged run — 2026-10-26

Exploratory, operator request (hackathon); PLAN.md deviation 21 was committed as afd8510 before the first model call. Phase main; L1-L3 only; originally 5 repeats on each of two problems per rung. Amended 2026-10-27 00:00, operator: shortened to 2 repeats from L2 on; L1 has 5 repeats; stop rule unchanged. All cached extra repeats are retained. Final grading is serial and makes no model calls; no existing generation process was started or stopped during closeout.

Decided: grade only Grok entries with bench.grade_all.main(entries=..., output=results/2026-10-26-grok-function.jsonl). Historical results files are not rebuilt. Historical results JSONL files are checked against their starting SHA-256 during closeout.

## Harness verification

CLI: grok 1.0.70. HOME is inherited; credentials were never inspected or handled. Each benchmark call uses a fresh empty mrb- temporary cwd.

Final GROK_FLAGS: `--output-format json --tools read_file --disallowed-tools read_file,search_tool,use_tool --no-subagents --disable-web-search --max-turns 1 --no-plan --verbatim --permission-mode dontAsk --no-leader`.

An empty tool allowlist and an unknown name (none) were inconclusive. Final filtering allows the known read_file tool, then removes read_file and the always-on search_tool/use_tool MCP meta-tools. Standalone mode avoids a shared leader. Source: https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-agent/src/tool_list.rs

Probe receipts: cache/grok_tool_probe.json and cache/grok_tool_probe02.json through cache/grok_tool_probe05.json. The first four requested a marker write; each left the temporary cwd empty and promised an action, so those replies alone were not accepted as proof. Probe 05 used the final flags with streaming-json to audit tool exposure: no tool-call events; final answer NO_TOOLS_AVAILABLE; stopReason end_turn. available_commands initially reports empty tools lists and later advertises the MCP discovery catalog; the catalog is not an executed tool call. The MCP meta-tools needed to invoke that catalog are removed by the denylist. Raw CLI stdout is retained locally under ignored cache/raw/.

The five verification calls cost $0.257960, included in the $25 Grok budget and excluded from benchmark pass counts. Token input totals include uncached input plus cached reads and cache writes, matching the Claude lane convention.

## Grades and rung costs

| Config | Rung | Passes/attempts (k/n) | Median s | Total $ | $/pass | Decision |
|---|---:|---:|---:|---:|---:|---|
| grok47-low | L1 | 10/10 | 20.206 | 0.472010 | 0.047201 | Climb |
| grok47-low | L2 | 10/10 | 28.904 | 0.537018 | 0.053702 | Climb |
| grok47-low | L3 | 3/4 | 38.931 | 0.232408 | 0.077469 | Stop: below 100% |
| grok47-medium | L1 | 10/10 | 27.319 | 0.511672 | 0.051167 | Climb |
| grok47-medium | L2 | 7/7 | 44.210 | 0.435500 | 0.062214 | Climb |
| grok47-medium | L3 | 3/4 | 127.308 | 0.382792 | 0.127597 | Stop: below 100% |
| grok47-high | L1 | 10/10 | 30.780 | 0.532366 | 0.053237 | Climb |
| grok47-high | L2 | 4/4 | 68.950 | 0.291436 | 0.072859 | Climb |
| grok47-high | L3 | 4/4 | 158.172 | 0.469498 | 0.117374 | L3 complete |
| grok47fast-low | L1 | 10/10 | 14.860 | 0.947420 | 0.094742 | Climb |
| grok47fast-low | L2 | 10/10 | 21.501 | 1.110104 | 0.111010 | Climb |
| grok47fast-low | L3 | 3/4 | 33.824 | 0.503128 | 0.167709 | Stop: below 100% |

## Per-config totals

| Config | Passes/attempts | Median s | Total $ | $/pass |
|---|---:|---:|---:|---:|
| grok47-low | 23/24 | 26.459 | 1.241436 | 0.053975 |
| grok47-medium | 20/21 | 32.562 | 1.329964 | 0.066498 |
| grok47-high | 18/18 | 40.966 | 1.293300 | 0.071850 |
| grok47fast-low | 23/24 | 19.384 | 2.560652 | 0.111333 |

Benchmark spend: **$6.425352** across **87** cached calls. Known Grok spend including verification and retained retries: **$6.683312 / $25.00**.

## Stop decisions

- grok47-low L3: 3/4; below 100%, stop rule fired.
- grok47-medium L3: 3/4; below 100%, stop rule fired.
- grok47fast-low L3: 3/4; below 100%, stop rule fired.
- grok47-high: 18/18 overall, including 4/4 at L3; no failure stop. All configs ended at L3; the $25 budget cap was not reached.

## Cached coverage retained

| Config | L1 repeats per problem | L2 ledger / taller-within repeats | L3 repeats per problem |
|---|---:|---:|---:|
| grok47-low | 5 / 5 | 5 / 5 | 2 / 2 |
| grok47-medium | 5 / 5 | 4 / 3 | 2 / 2 |
| grok47-high | 5 / 5 | 2 / 2 | 2 / 2 |
| grok47fast-low | 5 / 5 | 5 / 5 | 2 / 2 |

The possibly outstanding `grok47-high p06_calc r2` receipt was present in the grading snapshot and is included. No new model calls were made during closeout.

## Original L1 generation commands (historical; not rerun)

```sh
python3 -m bench.run --phase main --configs grok47-low --problems p01_overlap_minutes,p02_squash --repeats 1-5 --lanes 4
python3 -m bench.run --phase main --configs grok47-medium --problems p01_overlap_minutes,p02_squash --repeats 1-5 --lanes 4
python3 -m bench.run --phase main --configs grok47-high --problems p01_overlap_minutes,p02_squash --repeats 1-5 --lanes 4
python3 -m bench.run --phase main --configs grok47fast-low --problems p01_overlap_minutes,p02_squash --repeats 1-5 --lanes 4
```

Each group of config commands above is launched as background subprocesses by a single stage driver; the driver waits for every process before grading and selecting survivors.

## Grading command used after each rung

```python
import json
from pathlib import Path
from bench import grade_all
entries = [d for p in Path("cache/calls").glob("*.json")
           if (d := json.loads(p.read_text())).get("cli") == "grok"]
grade_all.main(entries=entries, output="results/2026-10-26-grok-function.jsonl")
```

## Reproduce pass counts

```sh
python3 - <<'PYCOUNT'
import collections, json
from pathlib import Path
groups = collections.defaultdict(list)
for line in Path("results/2026-10-26-grok-function.jsonl").read_text().splitlines():
    r = json.loads(line)
    groups[(r["config"], r["rung"])].append(r)
for (config, rung), rows in sorted(groups.items()):
    print(config, f"L{rung}", f"{sum(r["passed"] for r in rows)}/{len(rows)}")
PYCOUNT
```

## Preservation

All 15 historical results JSONL files (including nested appendix and pilot results) remain byte-identical to original branch commit `e3de82c`, verified by SHA-256. The only added results JSONL is `results/2026-10-26-grok-function.jsonl`. Report artifacts are regenerated separately.

| Historical results file | SHA-256 |
|---|---|
| `results/2026-10-22-pilot-agentic.jsonl` | `6a3ac4547055ec56a028acb1658758ff2b159d603226d69f4ae6d87a8545a345` |
| `results/2026-10-22-pilot.jsonl` | `ac4cc8e36810a16188a0a45fe4b48eca10a8f9ea0974070266f16e4047971f69` |
| `results/2026-10-22b-agentic.jsonl` | `28ab7a1e9e70733db8e0ffe984cc1867c0303894cac07e55c56b0370086692ce` |
| `results/2026-10-22b-function.jsonl` | `b547b04a39fbdfcd02b102ce40647a21c20dd8006ea4fb5fb06f5b83fe981772` |
| `results/2026-10-22b-trim.jsonl` | `b0fc58681b9f9ccaf74cea7f87f3aa062f493e5918afab1e46cb48eb03573afb` |
| `results/2026-10-25-isolated-agentic.jsonl` | `fef78227c24bfb1b15b0ebda7b00d8337927ac2f77ff017dbba98f3f58fd3b5b` |
| `results/appendix/codex_harness.jsonl` | `5bf8288a66bf2efa931316c1834e82ec5fb0ffa8019cf49f816bdf75d9b1752e` |
| `results/appendix/harness_bias.jsonl` | `a61ae36c295a5eb28358163f0f6936591345969aceac52afd3d34bbb6651fcf3` |
| `results/appendix/isolation/function.jsonl` | `57b6721db0d5ef952e314a80f140ae94643e3e7b7dac3371d6603c3f7c134213` |
| `results/appendix/isolation/hard.jsonl` | `b0943d64023be6e4f0c6cd62560d416a37655a8cb915e752e13bf27034814b82` |
| `results/appendix/isolation/harness_bias.jsonl` | `9c24bfd9515243565134726d4026e459f2d2983f462eb568cbe2c8b6942dd536` |
| `results/appendix/isolation/main.jsonl` | `fc280388ea314fa8569eaf84c3c0555ab6e4dcb60019de7ab18a7bed941ff34a` |
| `results/appendix/isolation/rescue.jsonl` | `59879f5adedd7a46b9304956a744b9f1fd78e39e4cfa227312eb88adc3d8dad9` |
| `results/appendix/luna_rescue.jsonl` | `474d863c880d840fc99acb5446b5219268fcddd884de20ec08f02cb6b217c2e5` |
| `results/quality.jsonl` | `67a5f24651a2366f5f37ead0250d9eb59131ab37c76c85e533b5e76eec8ea747` |
