# Inkling 2 Mini on DispatchBench p01-p15 (2026-11-22)

Free local CPU model (i7-8700 6C/12T, ~63 GiB RAM, no GPU), llama.cpp b12600, IQ4_NL GGUF. **Not comparable on latency** with the API lanes; no price (cost 0).
Settings (frozen after p01 tuning, sources in `inkling/SETTINGS_NOTES.md`; tuning in `inkling/TUNING_LOG.md`): `llama-server --jinja -c 32768 -t 6 -tb 6 -np 1`, temp 1.0, top_k 50, top_p 1.0, min_p 0, default thinking effort (high, 0.9). One repeat, tasks run sequentially, frozen grader.

## Primary result (max_tokens 12288): **7/15**
Total generation wall time 9h00m (9.01 h); median 48.0 min per task.

| problem | rung | outcome | wall | out tok | gen tok/s | peak RSS GiB | load avg |
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

