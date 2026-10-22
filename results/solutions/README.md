# Graded solutions

Every completion that was graded, as the code the grader saw. Browse `<problem>/index.md` for a table per problem (outcome, grade detail, size, and quality metrics when `results/quality.jsonl` exists).

Layout: `<problem>/<config>/<phase>-r<repeat>.py`. The phase is in the name because the same config, problem and repeat can occur in several phases (calibration, main, hard, escalation, exploratory). Warmup calls are not exported.

Each file is byte-identical to the code that was graded: it is the output of `bench.grade_all.extract` on the cached completion, with no header added. `python3 -m analysis.export_solutions` recomputes the grade key `sha256(problem_file_hash16 + NUL + code)` for every file and fails unless `cache/grades/<key>.json` exists (harness errors and empty completions have no cached grade). Output is deterministic; re-running leaves no diff.

Files by phase: F build 70, G build 70, G repair 87, calibration 30, escalation 15, exploratory 105, hard 60, main 360. Total 797.

Post-hoc appendix F/G completions are exported when their cache entries hold text; other appendix arms contain summary rows only.

Passes per config (pass / graded, all phases):

| problem | rung | haiku-low | haiku-low-plan+luna-high-bare | haiku-low-plan+luna-low | haiku-medium | luna-high | luna-high-bare+haiku-on-fail | luna-high-bare+haiku-review-all | luna-high-bare+retry-on-fail | luna-low | luna-low+haiku-on-fail | luna-low+haiku-review-all | luna-low-bare | luna-medium | sol61-medium | sonnet-medium |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [p01_overlap_minutes](p01_overlap_minutes/index.md) | L1 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 6/6 | 6/6 |
| [p02_squash](p02_squash/index.md) | L1 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 6/6 | 6/6 |
| [p03_ledger](p03_ledger/index.md) | L2 | 6/6 | 5/5 | 4/5 | 5/5 | 5/5 | - | 5/5 | - | 5/5 | - | 5/5 | 3/5 | 4/5 | 6/6 | 6/6 |
| [p04_taller_within](p04_taller_within/index.md) | L2 | 6/6 | 5/5 | 5/5 | 5/5 | 5/5 | - | 5/5 | - | 1/5 | 4/4 | 5/5 | 1/5 | 1/5 | 6/6 | 6/6 |
| [p05_pass_route](p05_pass_route/index.md) | L3 | 6/6 | - | - | 4/5 | 4/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 6/6 | 6/6 |
| [p06_calc](p06_calc/index.md) | L3 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 6/6 | 6/6 |
| [p07_weighted_distance_sums](p07_weighted_distance_sums/index.md) | L4 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 6/6 | 6/6 |
| [p08_recur](p08_recur/index.md) | L4 | 6/6 | 5/5 | 5/5 | 5/5 | 5/5 | - | 5/5 | - | 4/5 | - | 5/5 | 4/5 | 5/5 | 6/6 | 6/6 |
| [p09_k_machine_schedule](p09_k_machine_schedule/index.md) | L5 | 4/6 | 5/5 | 4/5 | 5/5 | 4/5 | - | 5/5 | - | 2/5 | 1/1 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p10_avoid_count](p10_avoid_count/index.md) | L5 | 6/6 | 5/5 | 3/5 | 5/5 | 4/5 | - | 5/5 | - | 5/5 | 1/1 | 5/5 | 4/5 | 5/5 | 6/6 | 6/6 |
| [p11_best_average](p11_best_average/index.md) | L6 | 5/5 | 3/5 | 5/5 | 5/5 | 5/5 | - | 5/5 | - | 4/5 | 3/3 | 5/5 | 2/5 | 2/5 | 5/5 | 5/5 |
| [p12_sheet](p12_sheet/index.md) | L6 | 4/5 | 3/5 | 4/5 | 5/5 | 3/5 | 2/2 | 5/5 | 2/2 | 0/5 | 4/4 | 4/5 | 0/5 | 0/5 | 3/5 | 5/5 |
| [p13_xor_ring](p13_xor_ring/index.md) | L7 | 5/5 | - | - | - | 5/5 | - | - | - | - | - | - | - | - | 5/5 | 5/5 |
| [p14_bounce_board](p14_bounce_board/index.md) | L7 | 5/5 | - | - | - | 5/5 | - | - | - | - | - | - | - | - | 5/5 | 5/5 |
| [p15_paint_erase](p15_paint_erase/index.md) | L7 | 2/5 | - | - | - | 5/5 | - | - | - | - | - | - | - | - | 5/5 | 5/5 |
