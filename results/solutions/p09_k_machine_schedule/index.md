# p09_k_machine_schedule

Rung L5. Signature: `def k_machine_schedule(jobs: list[list[int]], k: int) -> int:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 52 | 72 | 20 | 0 | 1.59 vs 1.95 | 1.00 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | timeout | large case 1: timeout | 47 | 76 | 7 | 2 | - vs - | - | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 52 | 70 | 19 | 0 | 1.82 vs 1.95 | 1.00 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 54 | 73 | 17 | 0 | 1.89 vs 1.95 | 1.02 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | timeout | large case 1: 9.58s > limit 2.00s | 19 | 25 | 9 | 0 | - vs - | - | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 56 | 77 | 18 | 0 | 1.87 vs 1.95 | 0.94 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-low-plan+luna-high-bare | f-build | 1 | pass |  | 45 | 56 | - | - | - vs - | - | [f-build-r1.py](haiku-low-plan+luna-high-bare/f-build-r1.py) |
| haiku-low-plan+luna-high-bare | f-build | 2 | pass |  | 62 | 78 | - | - | - vs - | - | [f-build-r2.py](haiku-low-plan+luna-high-bare/f-build-r2.py) |
| haiku-low-plan+luna-high-bare | f-build | 3 | pass |  | 60 | 72 | - | - | - vs - | - | [f-build-r3.py](haiku-low-plan+luna-high-bare/f-build-r3.py) |
| haiku-low-plan+luna-high-bare | f-build | 4 | pass |  | 59 | 74 | - | - | - vs - | - | [f-build-r4.py](haiku-low-plan+luna-high-bare/f-build-r4.py) |
| haiku-low-plan+luna-high-bare | f-build | 5 | pass |  | 53 | 66 | - | - | - vs - | - | [f-build-r5.py](haiku-low-plan+luna-high-bare/f-build-r5.py) |
| haiku-low-plan+luna-low | f-build | 1 | pass |  | 47 | 59 | - | - | - vs - | - | [f-build-r1.py](haiku-low-plan+luna-low/f-build-r1.py) |
| haiku-low-plan+luna-low | f-build | 2 | pass |  | 65 | 84 | - | - | - vs - | - | [f-build-r2.py](haiku-low-plan+luna-low/f-build-r2.py) |
| haiku-low-plan+luna-low | f-build | 3 | crash |  | 60 | 72 | - | - | - vs - | - | [f-build-r3.py](haiku-low-plan+luna-low/f-build-r3.py) |
| haiku-low-plan+luna-low | f-build | 4 | pass |  | 57 | 71 | - | - | - vs - | - | [f-build-r4.py](haiku-low-plan+luna-low/f-build-r4.py) |
| haiku-low-plan+luna-low | f-build | 5 | pass |  | 50 | 65 | - | - | - vs - | - | [f-build-r5.py](haiku-low-plan+luna-low/f-build-r5.py) |
| haiku-medium | main | 1 | pass |  | 61 | 79 | 19 | 0 | 1.98 vs 1.95 | 0.70 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 46 | 62 | 17 | 0 | 1.95 vs 1.95 | 1.02 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 56 | 78 | 18 | 0 | 1.90 vs 1.95 | 0.94 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 54 | 69 | 20 | 6 | 2.05 vs 1.95 | 0.71 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 52 | 72 | 18 | 0 | 1.99 vs 1.95 | 1.00 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 68 | 83 | 23 | 0 | 0.84 vs 1.95 | 1.21 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 63 | 77 | 21 | 0 | 1.09 vs 1.95 | 1.24 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 53 | 64 | 18 | 0 | 1.76 vs 1.95 | 0.92 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | crash | small case 2: IndexError: list assignment index out of range | 54 | 67 | 17 | 0 | - vs - | - | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 50 | 61 | 16 | 0 | 1.69 vs 1.95 | 1.02 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-high-bare+haiku-on-fail | g-build | 1 | cached |  | 52 | 65 | - | - | - vs - | - | [g-build-r1.py](luna-high-bare+haiku-on-fail/g-build-r1.py) |
| luna-high-bare+haiku-on-fail | g-build | 2 | cached |  | 41 | 50 | - | - | - vs - | - | [g-build-r2.py](luna-high-bare+haiku-on-fail/g-build-r2.py) |
| luna-high-bare+haiku-on-fail | g-build | 3 | cached |  | 41 | 50 | - | - | - vs - | - | [g-build-r3.py](luna-high-bare+haiku-on-fail/g-build-r3.py) |
| luna-high-bare+haiku-on-fail | g-build | 4 | cached |  | 46 | 56 | - | - | - vs - | - | [g-build-r4.py](luna-high-bare+haiku-on-fail/g-build-r4.py) |
| luna-high-bare+haiku-on-fail | g-build | 5 | cached |  | 47 | 57 | - | - | - vs - | - | [g-build-r5.py](luna-high-bare+haiku-on-fail/g-build-r5.py) |
| luna-high-bare+haiku-review-all | g-repair | 1 | pass |  | 56 | 70 | - | - | - vs - | - | [g-repair-r1.py](luna-high-bare+haiku-review-all/g-repair-r1.py) |
| luna-high-bare+haiku-review-all | g-repair | 2 | pass |  | 41 | 50 | - | - | - vs - | - | [g-repair-r2.py](luna-high-bare+haiku-review-all/g-repair-r2.py) |
| luna-high-bare+haiku-review-all | g-repair | 3 | pass |  | 41 | 50 | - | - | - vs - | - | [g-repair-r3.py](luna-high-bare+haiku-review-all/g-repair-r3.py) |
| luna-high-bare+haiku-review-all | g-repair | 4 | pass |  | 52 | 65 | - | - | - vs - | - | [g-repair-r4.py](luna-high-bare+haiku-review-all/g-repair-r4.py) |
| luna-high-bare+haiku-review-all | g-repair | 5 | pass |  | 49 | 60 | - | - | - vs - | - | [g-repair-r5.py](luna-high-bare+haiku-review-all/g-repair-r5.py) |
| luna-low | main | 1 | wrong | small case 0 | 14 | 17 | 4 | 0 | - vs - | - | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | timeout | small cases: timeout | 52 | 63 | 23 | 0 | - vs - | - | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 52 | 67 | 18 | 0 | 1.51 vs 1.95 | 1.20 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 51 | 66 | 17 | 0 | 1.58 vs 1.95 | 1.20 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | timeout | small cases: timeout | 58 | 75 | 23 | 0 | - vs - | - | [main-r5.py](luna-low/main-r5.py) |
| luna-low+haiku-on-fail | g-build | 1 | cached |  | 50 | 65 | - | - | - vs - | - | [g-build-r1.py](luna-low+haiku-on-fail/g-build-r1.py) |
| luna-low+haiku-on-fail | g-build | 2 | cached |  | 48 | 61 | - | - | - vs - | - | [g-build-r2.py](luna-low+haiku-on-fail/g-build-r2.py) |
| luna-low+haiku-on-fail | g-build | 3 | cached |  | 49 | 65 | - | - | - vs - | - | [g-build-r3.py](luna-low+haiku-on-fail/g-build-r3.py) |
| luna-low+haiku-on-fail | g-build | 4 | cached |  | 51 | 69 | - | - | - vs - | - | [g-build-r4.py](luna-low+haiku-on-fail/g-build-r4.py) |
| luna-low+haiku-on-fail | g-build | 5 | cached |  | 49 | 63 | - | - | - vs - | - | [g-build-r5.py](luna-low+haiku-on-fail/g-build-r5.py) |
| luna-low+haiku-on-fail | g-repair | 5 | pass |  | 60 | 81 | - | - | - vs - | - | [g-repair-r5.py](luna-low+haiku-on-fail/g-repair-r5.py) |
| luna-low+haiku-review-all | g-repair | 1 | pass |  | 48 | 67 | - | - | - vs - | - | [g-repair-r1.py](luna-low+haiku-review-all/g-repair-r1.py) |
| luna-low+haiku-review-all | g-repair | 2 | pass |  | 48 | 61 | - | - | - vs - | - | [g-repair-r2.py](luna-low+haiku-review-all/g-repair-r2.py) |
| luna-low+haiku-review-all | g-repair | 3 | pass |  | 57 | 76 | - | - | - vs - | - | [g-repair-r3.py](luna-low+haiku-review-all/g-repair-r3.py) |
| luna-low+haiku-review-all | g-repair | 4 | pass |  | 51 | 70 | - | - | - vs - | - | [g-repair-r4.py](luna-low+haiku-review-all/g-repair-r4.py) |
| luna-low+haiku-review-all | g-repair | 5 | pass |  | 58 | 77 | - | - | - vs - | - | [g-repair-r5.py](luna-low+haiku-review-all/g-repair-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 46 | 58 | 15 | 0 | 1.51 vs 1.95 | 1.20 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | pass |  | 46 | 57 | 15 | 0 | 1.87 vs 1.95 | 1.20 | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 58 | 74 | 24 | 1 | 1.08 vs 1.95 | 1.03 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 49 | 64 | 17 | 0 | 1.70 vs 1.95 | 1.20 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 50 | 64 | 17 | 0 | 1.24 vs 1.95 | 1.20 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 55 | 71 | 19 | 0 | 1.52 vs 1.95 | 1.20 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 49 | 63 | 16 | 0 | 1.74 vs 1.95 | 0.94 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 47 | 62 | 15 | 0 | 1.80 vs 1.95 | 1.21 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 51 | 65 | 18 | 0 | 1.51 vs 1.95 | 1.20 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 62 | 79 | 25 | 0 | 0.98 vs 1.95 | 1.21 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 64 | 80 | 22 | 0 | 0.94 vs 1.95 | 1.21 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 63 | 82 | 22 | 0 | 0.89 vs 1.95 | 1.30 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 59 | 76 | 22 | 0 | 1.04 vs 1.95 | 1.11 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 60 | 76 | 22 | 0 | 0.95 vs 1.95 | 1.30 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 60 | 77 | 22 | 0 | 0.82 vs 1.95 | 1.29 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 60 | 76 | 22 | 0 | 0.93 vs 1.95 | 1.29 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 55 | 61 | 18 | 0 | 1.83 vs 1.95 | 1.02 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 65 | 71 | 17 | 0 | 1.45 vs 1.95 | 0.69 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 59 | 63 | 18 | 4 | 1.62 vs 1.95 | 0.69 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 54 | 59 | 18 | 0 | 1.79 vs 1.95 | 1.02 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 65 | 70 | 17 | 0 | 1.84 vs 1.95 | 0.69 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 54 | 60 | 18 | 0 | 1.73 vs 1.95 | 1.02 | [main-r5.py](sonnet-medium/main-r5.py) |
