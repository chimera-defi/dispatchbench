# Inkling 2 Mini on DispatchBench p01-p15 (2026-11-22)

Local CPU model (i7-8700 6C/12T, ~63 GiB RAM, no GPU), llama.cpp b12600, IQ4_NL GGUF. **Not comparable on latency** with the API lanes; no list price.
**Cost is estimated from box-hours**, not metered: wall time at the rate of Hetzner auction box eth2-3 (EUR 52.17 a month over 744 h = EUR 0.0701 an hour; $0.0767 an hour at 1.0939 dollars per euro, ECB 2026-11-23).
Settings (frozen after p01 tuning, sources in `inkling/SETTINGS_NOTES.md`; tuning in `inkling/TUNING_LOG.md`): `llama-server --jinja -c 32768 -t 6 -tb 6 -np 1`, temp 1.0, top_k 50, top_p 1.0, min_p 0, default thinking effort (high, 0.9). One repeat, tasks run sequentially, frozen grader. Each task is capped at 12288 generated tokens, which the API lanes are not; every `no_code (length)` row below means the model was still thinking at the cap and wrote no final code, so those are token-budget failures, not wrong answers. One server process served all tasks, so the memory column is a running high-water mark. The load column is the 1-minute load average at task start; other host processes pushed it to 12-25 during p15 (2.2 tok/s vs 4-5 elsewhere), so p15's time is inflated.

## Primary result (max_tokens 12288): **7/15**
Total generation wall time 9h00m (9.01 h); median 48.0 min per task. Estimated cost $0.69, $0.099 per pass (9.01 h x $0.0767 an hour).

| problem | rung | outcome | wall | out tok | gen tok/s | server peak RSS so far GiB (VmHWM, cumulative, includes mapped weights) | load avg |
|---|---|---|---|---|---|---|---|
| p01_overlap_minutes | L1 | pass | 6.1 min | 1821 | 5.2 | 28.8 | 3.58 |
| p02_squash | L1 | pass | 3.8 min | 1134 | 5.3 | 29.1 | 6.64 |
| p03_ledger | L2 | pass | 21.5 min | 5745 | 4.7 | 29.5 | 9.07 |
| p04_taller_within | L2 | pass | 11.1 min | 3291 | 5.1 | 30.0 | 9.48 |
| p05_pass_route | L3 | pass | 9.3 min | 2726 | 5.1 | 30.3 | 6.06 |
| p06_calc | L3 | no_code (length) | 48.7 min | 12288 | 4.3 | 30.7 | 6.36 |
| p07_weighted_distance_sums | L4 | pass | 11.4 min | 3397 | 5.1 | 31.3 | 6.37 |
| p08_recur | L4 | pass | 43.0 min | 11021 | 4.3 | 31.8 | 5.65 |
| p09_k_machine_schedule | L5 | no_code (length) | 48.0 min | 12288 | 4.3 | 32.4 | 5.92 |
| p10_avoid_count | L5 | no_code (length) | 48.3 min | 12288 | 4.3 | 33.0 | 6.60 |
| p11_best_average | L6 | no_code (length) | 50.1 min | 12288 | 4.1 | 33.6 | 8.44 |
| p12_sheet | L6 | no_code (length) | 50.7 min | 12288 | 4.1 | 34.5 | 6.35 |
| p13_xor_ring | L7 | no_code (length) | 48.9 min | 12288 | 4.2 | 35.1 | 6.27 |
| p14_bounce_board | L7 | no_code (length) | 48.2 min | 12288 | 4.3 | 35.1 | 9.64 |
| p15_paint_erase | L7 | no_code (length) | 91.6 min | 12288 | 2.2 | 35.1 | 6.43 |

## Secondary: retry ladder on the tasks that were capped at 12288 (labelled; the primary above stays the headline)
The operator asked for a retry of the capped tasks. Stage 1: thinking effort medium (0.7, `chat_template_kwargs.reasoning_effort`) at max_tokens 16384 on every capped task. Stage 2: effort low (0.2) at 16384 on the tasks still capped. Stage 3: default effort at 24576 on the task still capped. A task moves to the next stage only if it ended `no_code` at the cap; a wrong or crashing answer ends the ladder for that task. Same server flags, sampling and grader as the primary. Host load at task start was 5.7-14.8 during these runs (3.0-4.5 tok/s, slower than the primary), so times are inflated by other host processes.

**Ladder result: 13/15** (primary passes + best ladder outcome per task). This mixes settings per task, so it is a secondary figure, not a single-configuration score. Retry wall time 11h04m (11.07 h); primary + retries 20h04m (20.08 h). Estimated cost $1.54, $0.118 per pass (20.08 h x $0.0767 an hour).

### Stage `inkling2mini-medium16k` (effort medium, max_tokens 16384): 5/8 pass

| problem | rung | outcome | wall | out tok | gen tok/s | server peak RSS so far GiB (VmHWM, cumulative, includes mapped weights) | load avg |
|---|---|---|---|---|---|---|---|
| p06_calc | L3 | pass | 45.8 min | 8053 | 3.0 | 29.0 | 9.59 |
| p09_k_machine_schedule | L5 | pass | 29.2 min | 5379 | 3.1 | 29.5 | 8.36 |
| p10_avoid_count | L5 | pass | 48.9 min | 9764 | 3.3 | 29.8 | 7.78 |
| p11_best_average | L6 | no_code (length) | 81.0 min | 16384 | 3.4 | 30.3 | 14.83 |
| p12_sheet | L6 | no_code (length) | 75.0 min | 16384 | 3.7 | 30.3 | 9.35 |
| p13_xor_ring | L7 | pass | 31.7 min | 8503 | 4.5 | 31.1 | 6.58 |
| p14_bounce_board | L7 | pass | 63.0 min | 15046 | 4.0 | 31.6 | 6.69 |
| p15_paint_erase | L7 | wrong (stop) | 62.0 min | 14916 | 4.0 | 32.2 | 6.51 |

### Stage `inkling2mini-low16k` (effort low, max_tokens 16384): 0/2 pass

| problem | rung | outcome | wall | out tok | gen tok/s | server peak RSS so far GiB (VmHWM, cumulative, includes mapped weights) | load avg |
|---|---|---|---|---|---|---|---|
| p11_best_average | L6 | no_code (length) | 80.0 min | 16384 | 3.4 | 28.8 | 5.72 |
| p12_sheet | L6 | crash (stop) | 33.1 min | 6411 | 3.5 | 28.8 | 9.35 |

### Stage `inkling2mini-default24k` (effort default, max_tokens 24576): 1/1 pass

| problem | rung | outcome | wall | out tok | gen tok/s | server peak RSS so far GiB (VmHWM, cumulative, includes mapped weights) | load avg |
|---|---|---|---|---|---|---|---|
| p11_best_average | L6 | pass | 114.4 min | 21220 | 3.1 | 28.8 | 8.52 |

