# Graded solutions

Start with the table: each problem folder has a `README.md` (summary, expected approach, how to verify) and an `index.md` (every answer).

| problem | set | answers | pass | what to check |
|---|---|---|---|---|
| [p01_overlap_minutes](p01_overlap_minutes/README.md) | main L1-L6 | 63 | 63 | Total minutes (half-open intervals) covered by at least k meetings at once. |
| [p02_squash](p02_squash/README.md) | main L1-L6 | 63 | 63 | Run-length encode a string; runs of 1-2 are written out, runs of 3+ become count + char; digits and backslash are escaped. |
| [p03_ledger](p03_ledger/README.md) | main L1-L6 | 83 | 79 | Simulate bank operations with freeze rules and undo; return final balances and the indices of failed ops. |
| [p04_taller_within](p04_taller_within/README.md) | main L1-L6 | 87 | 73 | For each position, count strictly taller people among the k directly in front. |
| [p05_pass_route](p05_pass_route/README.md) | main L1-L6 | 63 | 61 | Cheapest trip from stop 0 to n-1 where zone passes can be bought at listed stations to make that zone's rides free. |
| [p06_calc](p06_calc/README.md) | main L1-L6 | 63 | 58 | Evaluate an integer expression with + - * / % ^, unary minus and parentheses; return the int or "error". |
| [p07_weighted_distance_sums](p07_weighted_distance_sums/README.md) | main L1-L6 | 63 | 61 | For every tree node v, sum over nodes u of w[u] * dist(u, v). |
| [p08_recur](p08_recur/README.md) | main L1-L6 | 83 | 81 | Expand a calendar recurrence rule (daily, weekly, monthly by day or by nth weekday, yearly) into the first count dates. |
| [p09_k_machine_schedule](p09_k_machine_schedule/README.md) | main L1-L6 | 84 | 77 | Max total pay of jobs that fit on k identical machines (half-open intervals). |
| [p10_avoid_count](p10_avoid_count/README.md) | main L1-L6 | 84 | 79 | Count length-n strings over a small alphabet that contain no banned substring, mod 1e9+7, with n up to 10**18. |
| [p11_best_average](p11_best_average/README.md) | main L1-L6 | 83 | 74 | Largest average over contiguous subarrays of length >= k, as an exact reduced fraction. |
| [p12_sheet](p12_sheet/README.md) | main L1-L6 | 88 | 58 | Evaluate a spreadsheet of integers and formulas (SUM/MIN/MAX/IF, ranges) with #DIV/0! and #CYCLE! errors. |
| [p13_xor_ring](p13_xor_ring/README.md) | hard L7 | 40 | 37 | Apply a XOR-of-offsets update to a ring of lamps t times (t up to 10**18). |
| [p14_bounce_board](p14_bounce_board/README.md) | hard L7 | 40 | 32 | Expected number of turns to finish a dice board with bounce-back and jumps, as an exact fraction, or None if the game may never end. |
| [p15_paint_erase](p15_paint_erase/README.md) | hard L7 | 40 | 33 | Apply paint-if-not-darker and erase operations to a strip of up to 10**9 cells; report cell counts per colour. |
| [candy](candy/README.md) | pilot | 21 | 21 | Candy: minimum candies so each child gets at least one and a higher rating than a neighbour gets more. |
| [course2](course2/README.md) | pilot | 21 | 21 | Course Schedule II: return a valid order of courses given prerequisites, or [] if there is a cycle. |
| [fizzbuzz](fizzbuzz/README.md) | pilot | 27 | 27 | Return 1..n as strings, with Fizz, Buzz and FizzBuzz for multiples of 3, 5 and 15. |
| [itinerary](itinerary/README.md) | pilot | 0 | 0 | code not recoverable |
| [minwindow](minwindow/README.md) | pilot | 0 | 0 | code not recoverable |
| [wildcard](wildcard/README.md) | pilot | 0 | 0 | code not recoverable |

Pilot problems (fizzbuzz, course2, candy, itinerary, minwindow, wildcard) are graded by `bench/pilot/checker.py` from the row's own `passed`, not by the grade-key check below. Only the trim-probe answers kept their code; the 205 main pilot rows and the repo-task pilot do not. The per-config table below covers p01-p15 only.

Every completion that was graded, as the code the grader saw. Browse `<problem>/index.md` for a table per problem (outcome, grade detail, size, and quality metrics when `results/quality.jsonl` exists).

Layout: `<problem>/<config>/<phase>-r<repeat>.py`. The phase is in the name because the same config, problem and repeat can occur in several phases (calibration, main, hard, escalation, exploratory). Warmup calls are not exported.

Each file is byte-identical to the code that was graded: it is the output of `bench.grade_all.extract` on the cached completion, with no header added. `python3 -m analysis.export_solutions` recomputes the grade key `sha256(problem_file_hash16 + NUL + code)` for every file and fails unless `cache/grades/<key>.json` exists (harness errors and empty completions have no cached grade). Output is deterministic; re-running leaves no diff.

Files by phase: F build 70, G build 70, G repair 87, calibration 30, escalation 15, exploratory 345, hard 120, main 360, pilot-trim 69. Total 1166.

Post-hoc appendix F/G completions are exported when their cache entries hold text; other appendix arms contain summary rows only.

Passes per config (pass / graded, all phases):

| problem | rung | astra-medium | haiku-low | haiku-low-plan+luna-high-bare | haiku-low-plan+luna-low | haiku-medium | luna-high | luna-high-bare+haiku-on-fail | luna-high-bare+haiku-review-all | luna-high-bare+retry-on-fail | luna-low | luna-low+haiku-on-fail | luna-low+haiku-review-all | luna-low-bare | luna-medium | luna56-high | luna56-low | sol56-high | sol61-medium | sonnet-medium |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [p01_overlap_minutes](p01_overlap_minutes/index.md) | L1 | 5/5 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p02_squash](p02_squash/index.md) | L1 | 5/5 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p03_ledger](p03_ledger/index.md) | L2 | 5/5 | 6/6 | 5/5 | 4/5 | 5/5 | 5/5 | - | 5/5 | - | 5/5 | - | 5/5 | 3/5 | 4/5 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p04_taller_within](p04_taller_within/index.md) | L2 | 5/5 | 6/6 | 5/5 | 5/5 | 5/5 | 5/5 | - | 5/5 | - | 1/5 | 4/4 | 5/5 | 1/5 | 1/5 | 4/5 | 4/5 | 5/5 | 6/6 | 6/6 |
| [p05_pass_route](p05_pass_route/index.md) | L3 | 5/5 | 6/6 | - | - | 4/5 | 4/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p06_calc](p06_calc/index.md) | L3 | 5/5 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 4/5 | 1/5 | 5/5 | 6/6 | 6/6 |
| [p07_weighted_distance_sums](p07_weighted_distance_sums/index.md) | L4 | 5/5 | 6/6 | - | - | 5/5 | 5/5 | - | - | - | 5/5 | - | - | 5/5 | 5/5 | 5/5 | 3/5 | 5/5 | 6/6 | 6/6 |
| [p08_recur](p08_recur/index.md) | L4 | 5/5 | 6/6 | 5/5 | 5/5 | 5/5 | 5/5 | - | 5/5 | - | 4/5 | - | 5/5 | 4/5 | 5/5 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p09_k_machine_schedule](p09_k_machine_schedule/index.md) | L5 | 5/5 | 4/6 | 5/5 | 4/5 | 5/5 | 4/5 | - | 5/5 | - | 2/5 | 1/1 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 | 6/6 | 6/6 |
| [p10_avoid_count](p10_avoid_count/index.md) | L5 | 5/5 | 6/6 | 5/5 | 3/5 | 5/5 | 4/5 | - | 5/5 | - | 5/5 | 1/1 | 5/5 | 4/5 | 5/5 | 5/5 | 4/5 | 5/5 | 6/6 | 6/6 |
| [p11_best_average](p11_best_average/index.md) | L6 | 5/5 | 5/5 | 3/5 | 5/5 | 5/5 | 5/5 | - | 5/5 | - | 4/5 | 3/3 | 5/5 | 2/5 | 2/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| [p12_sheet](p12_sheet/index.md) | L6 | 5/5 | 4/5 | 3/5 | 4/5 | 5/5 | 3/5 | 2/2 | 5/5 | 2/2 | 0/5 | 4/4 | 4/5 | 0/5 | 0/5 | 3/5 | 1/5 | 5/5 | 3/5 | 5/5 |
| [p13_xor_ring](p13_xor_ring/index.md) | L7 | 5/5 | 5/5 | - | - | - | 5/5 | - | - | - | - | - | - | - | - | 4/5 | 3/5 | 5/5 | 5/5 | 5/5 |
| [p14_bounce_board](p14_bounce_board/index.md) | L7 | 5/5 | 5/5 | - | - | - | 5/5 | - | - | - | - | - | - | - | - | 2/5 | 2/5 | 3/5 | 5/5 | 5/5 |
| [p15_paint_erase](p15_paint_erase/index.md) | L7 | 5/5 | 2/5 | - | - | - | 5/5 | - | - | - | - | - | - | - | - | 3/5 | 3/5 | 5/5 | 5/5 | 5/5 |
