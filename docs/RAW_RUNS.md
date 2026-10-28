# Raw run index

Each Run rows entry is one JSONL file. `Rows` = non-empty lines, including malformed JSON and non-object values.
Files stay at their committed paths. Verify a file from the repo root with `sha256sum <path>`.
For a folder, hash each included file. Use paths relative to that folder, without a leading `./`.
The aggregate is SHA-256 over lexically sorted lines of `<sha256>  <relpath>\n`, encoded as UTF-8.
The walker skips root `.gitignore` entries and `__pycache__`; it includes untracked files.
Run this one-line shell command from the repo root (change `d` for another folder):

```bash
d=cache/calls; python3 -c 'from analysis.raw_runs import published_files, ROOT; import sys; d=ROOT/sys.argv[1]; print("\n".join(p.relative_to(d).as_posix() for p in published_files(d)))' "$d" | (cd "$d" && while IFS= read -r f; do [ -z "$f" ] || sha256sum "$f"; done) | LC_ALL=C sort | sha256sum
```

## Run rows

Run is the path relative to `results/`, without `.jsonl`. Date uses the filename first, then the earliest recorded timestamp or date; `-` means no timestamp recorded. Lanes name CLI families.
Blank lines, malformed JSON and non-object values are skipped when deriving dates and lanes.

| Run | Date | Lane(s) | Rows | SHA-256 | Link |
|---|---|---|---:|---|---|
| 2026-10-22-pilot-agentic | 2026-10-22 | claude, codex | 6 | `6a3ac4547055ec56a028acb1658758ff2b159d603226d69f4ae6d87a8545a345` | [results/2026-10-22-pilot-agentic.jsonl](../results/2026-10-22-pilot-agentic.jsonl) |
| 2026-10-22-pilot | 2026-10-22 | claude, codex | 205 | `ac4cc8e36810a16188a0a45fe4b48eca10a8f9ea0974070266f16e4047971f69` | [results/2026-10-22-pilot.jsonl](../results/2026-10-22-pilot.jsonl) |
| 2026-10-22b-agentic | 2026-10-22 | claude, codex | 84 | `28ab7a1e9e70733db8e0ffe984cc1867c0303894cac07e55c56b0370086692ce` | [results/2026-10-22b-agentic.jsonl](../results/2026-10-22b-agentic.jsonl) |
| 2026-10-22b-function | 2026-10-22 | claude, codex | 1261 | `b547b04a39fbdfcd02b102ce40647a21c20dd8006ea4fb5fb06f5b83fe981772` | [results/2026-10-22b-function.jsonl](../results/2026-10-22b-function.jsonl) |
| 2026-10-22b-trim | 2026-10-22 | claude, codex | 69 | `b0fc58681b9f9ccaf74cea7f87f3aa062f493e5918afab1e46cb48eb03573afb` | [results/2026-10-22b-trim.jsonl](../results/2026-10-22b-trim.jsonl) |
| 2026-10-25-isolated-agentic | 2026-10-25 | codex | 48 | `fef78227c24bfb1b15b0ebda7b00d8337927ac2f77ff017dbba98f3f58fd3b5b` | [results/2026-10-25-isolated-agentic.jsonl](../results/2026-10-25-isolated-agentic.jsonl) |
| 2026-10-26-grok-function | 2026-10-26 | grok | 87 | `d8dffdbdc71eed6ee79592ef158a59eb67c73f877e289901aa513601b47783b9` | [results/2026-10-26-grok-function.jsonl](../results/2026-10-26-grok-function.jsonl) |
| 2026-10-27-grok-agentic | 2026-10-27 | grok | 16 | `7aae8f0d5064925573e70b76e0794c91fbffbd56b138006ebb23cc09a7456ed8` | [results/2026-10-27-grok-agentic.jsonl](../results/2026-10-27-grok-agentic.jsonl) |
| 2026-10-28-devin-function | 2026-10-28 | devin | 12 | `86470b9ea1726bf7b0c750172a4688536b99d67ba9367a392be8efa489fc90ca` | [results/2026-10-28-devin-function.jsonl](../results/2026-10-28-devin-function.jsonl) |
| 2026-10-28-grok-spectrum-function | 2026-10-28 | grok | 114 | `57aa2c9f2db6f95d280ea6930182ee87bae1f5bfb519c7d1d259b0b2dde9e965` | [results/2026-10-28-grok-spectrum-function.jsonl](../results/2026-10-28-grok-spectrum-function.jsonl) |
| 2026-10-28-terra-function | 2026-10-28 | codex | 144 | `99900e6c2ee5f7aceced99fa18e052c23a86f280c9116528ba78d947a52f010a` | [results/2026-10-28-terra-function.jsonl](../results/2026-10-28-terra-function.jsonl) |
| appendix/codex_harness | 2026-10-24 | claude, codex | 138 | `5bf8288a66bf2efa931316c1834e82ec5fb0ffa8019cf49f816bdf75d9b1752e` | [results/appendix/codex_harness.jsonl](../results/appendix/codex_harness.jsonl) |
| appendix/harness_bias | 2026-10-24 | claude, codex | 240 | `a61ae36c295a5eb28358163f0f6936591345969aceac52afd3d34bbb6651fcf3` | [results/appendix/harness_bias.jsonl](../results/appendix/harness_bias.jsonl) |
| appendix/isolation/function | 2026-10-25 | codex | 935 | `57b6721db0d5ef952e314a80f140ae94643e3e7b7dac3371d6603c3f7c134213` | [results/appendix/isolation/function.jsonl](../results/appendix/isolation/function.jsonl) |
| appendix/isolation/hard | 2026-10-25 | codex | 15 | `b0943d64023be6e4f0c6cd62560d416a37655a8cb915e752e13bf27034814b82` | [results/appendix/isolation/hard.jsonl](../results/appendix/isolation/hard.jsonl) |
| appendix/isolation/harness_bias | 2026-10-25 | codex | 60 | `9c24bfd9515243565134726d4026e459f2d2983f462eb568cbe2c8b6942dd536` | [results/appendix/isolation/harness_bias.jsonl](../results/appendix/isolation/harness_bias.jsonl) |
| appendix/isolation/main | 2026-10-25 | codex | 60 | `fc280388ea314fa8569eaf84c3c0555ab6e4dcb60019de7ab18a7bed941ff34a` | [results/appendix/isolation/main.jsonl](../results/appendix/isolation/main.jsonl) |
| appendix/isolation/rescue | - | claude, codex | 258 | `59879f5adedd7a46b9304956a744b9f1fd78e39e4cfa227312eb88adc3d8dad9` | [results/appendix/isolation/rescue.jsonl](../results/appendix/isolation/rescue.jsonl) |
| appendix/luna_rescue | - | claude, codex | 525 | `474d863c880d840fc99acb5446b5219268fcddd884de20ec08f02cb6b217c2e5` | [results/appendix/luna_rescue.jsonl](../results/appendix/luna_rescue.jsonl) |
| quality | - | claude, codex | 1140 | `67a5f24651a2366f5f37ead0250d9eb59131ab37c76c85e533b5e76eec8ea747` | [results/quality.jsonl](../results/quality.jsonl) |

## Repo-task pass counts

Two pass rules. Passed our hidden tests: our hidden suite passes against the delivered code. Task complete: hidden and visible tests (the delivered `tests/` directory) both pass.
Older rows lack `task_complete`; it is derived as `visible_pass and hidden_pass`.

| Run | Config | Passed our hidden tests | Task complete |
|---|---|---:|---:|
| 2026-10-22b-agentic | astra-medium | 12/12 | 12/12 |
| 2026-10-22b-agentic | haiku-high | 12/12 | 12/12 |
| 2026-10-22b-agentic | haiku-low | 12/12 | 12/12 |
| 2026-10-22b-agentic | luna-low | 12/12 | 11/12 |
| 2026-10-22b-agentic | sol61-high | 12/12 | 12/12 |
| 2026-10-22b-agentic | sol61-medium | 12/12 | 12/12 |
| 2026-10-22b-agentic | sonnet-medium | 12/12 | 12/12 |
| 2026-10-25-isolated-agentic | astra-medium | 12/12 | 12/12 |
| 2026-10-25-isolated-agentic | luna-low | 12/12 | 7/12 |
| 2026-10-25-isolated-agentic | sol61-high | 12/12 | 12/12 |
| 2026-10-25-isolated-agentic | sol61-medium | 12/12 | 12/12 |
| 2026-10-27-grok-agentic | grok47-high | 8/8 | 8/8 |
| 2026-10-27-grok-agentic | grok47-low | 8/8 | 8/8 |

## Supporting files

`manifest.json`, `summary.json` and `dataset.json` are regenerated by
[analysis.summarize](../analysis/summarize.py) and [analysis.dataset](../analysis/dataset.py).
Their hashes hold only for the commit you read. Regenerate this index after rebuilding them.

| File | SHA-256 |
|---|---|
| [results/manifest.json](../results/manifest.json) | `2c52bb58b511f8fbdaa4347250b890844f836ecc207371d6826f4f8c479b30d8` |
| [results/prices.json](../results/prices.json) | `f215215ae059ffe9eaaa7d907fe844246d72fa2af96ee242793f290d0514992c` |
| [results/agentic_tests.json](../results/agentic_tests.json) | `bbf0dda405ca67a8da3139325b59fdd780073888359b54382adb739bddada3b5` |
| [results/quality.jsonl](../results/quality.jsonl) | `67a5f24651a2366f5f37ead0250d9eb59131ab37c76c85e533b5e76eec8ea747` |
| [results/quality_meta.json](../results/quality_meta.json) | `c67ed4da24b626581c7c785eba9c82495c02a8d06253c17effa0845778027a55` |

## Raw call caches

| Folder | Holds | Files | Aggregate SHA-256 |
|---|---|---:|---|
| [cache/calls/](../cache/calls/) | Function completions, usage and call metadata | 1744 | `ef6dfb9dbaa02bf4070dc1bfa8f402d14f8a29929aa24356e1a270a5b63f286f` |
| [cache/agentic/](../cache/agentic/) | Repo-task verdicts, usage and test summaries | 100 | `67a617f8e8cf19f61a165e714eda6983a93c046e4f0818492a7f49ef2b16283d` |
| [cache/grades/](../cache/grades/) | Function verdicts and timing fractions | 1654 | `9a2ee00a2cd90f289da6ad79f91b69944311589e06c3b69c514c3b3cf5f17f43` |
| [cache/gated_repair/](../cache/gated_repair/) | Builds, visible-test gates and repair completions | 227 | `1d93ce9b6ddcef8778891e78cbc95ea05d64f7f352c4272a53ef4a1de24afa9f` |
| [cache/plan_first/](../cache/plan_first/) | Planner and builder completions | 105 | `b1a47b100de26699a3b2eafc7bc10f1659f5541d386fdcb363a369b91564f05a` |
| [cache/trim/](../cache/trim/) | Harness-trim probe completions and usage | 69 | `9e333cf6e3ac1c367167fd8e3ba6d83cf751e1833e488854d6332b270a8a07aa` |
| [results/solutions/](../results/solutions/) | Graded Python answers and per-problem indexes | 1209 | `dc7b47bf117e0870f21c12c336c043b8cf3bf1a1112f520215cdadd648e66066` |

## Not published, and why

- `cache/raw/` and `cache/codex_harness/raw/`: full CLI transcripts carry host context, instruction files and local paths. Never committed.
- `cache/agentic_raw/`: dropped from history on 2026-10-26 for the same reason. Do not restore.
- `cache/quality/`, `cache/expected/`, `cache/tmp/`, `cache/*.log` and `artifacts/`: scratch and logs, rebuilt by the runners.
- `results/review-sol61/review.bundle`: removed from the tree on 2026-10-28 because it contains a local home path and needs a parent commit outside public history, so it cannot be imported. Older commits still hold it. Read [the published review](../results/research/review-sol61/REVIEW.md) instead.

## Pending

Codex Terra (`gpt-6.1-terra`, `gpt-5.6-terra`) and Grok full-spectrum runs (branch `bench-runs`)
and Devin `swe-1-6-slow` runs (branch `devin-runs`) are not on main yet.
They will appear in the tables once landed and this file is regenerated.
Pilot and trim Terra rows and the staged Grok rows above are separate from these pending runs.

## Leak scan

The publication scan covered home paths, email addresses, API keys and tokens
(`sk-`, `sk-ant-`, `xai-`, `gh*_`, `AKIA`, JWTs and bearer tokens), private keys,
IP addresses, the host name, instruction-file text and internal project words.
Hits kept on purpose: the synthetic sandbox HOME for user `codex` set by
[bench/codex_harness.py](../bench/codex_harness.py); `github.com/xai-org` (public vendor source link);
Anthropic's noreply commit-trailer address in `.claude/workflows`; and
`chimera-defi` / `chimera_defi` (repo owner). This doc describes the path and address without repeating them.
