# p08_recur

Rung L4. Signature: `def recur(start: str, rule: str, count: int) -> list[str]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 96 | 107 | 36 | 1 | -0.15 vs 0.03 | 0.76 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 89 | 102 | 28 | 0 | 0.79 vs 0.03 | 0.71 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 80 | 95 | 6 | 0 | -0.15 vs 0.03 | 0.74 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 92 | 100 | 28 | 0 | -0.02 vs 0.03 | 0.77 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 87 | 101 | 23 | 2 | -0.03 vs 0.03 | 1.01 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 77 | 90 | 20 | 0 | -0.02 vs 0.03 | 0.73 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-low-plan+luna-high-bare | f-build | 1 | pass |  | 81 | 94 | - | - | - vs - | - | [f-build-r1.py](haiku-low-plan+luna-high-bare/f-build-r1.py) |
| haiku-low-plan+luna-high-bare | f-build | 2 | pass |  | 74 | 88 | - | - | - vs - | - | [f-build-r2.py](haiku-low-plan+luna-high-bare/f-build-r2.py) |
| haiku-low-plan+luna-high-bare | f-build | 3 | pass |  | 69 | 81 | - | - | - vs - | - | [f-build-r3.py](haiku-low-plan+luna-high-bare/f-build-r3.py) |
| haiku-low-plan+luna-high-bare | f-build | 4 | pass |  | 76 | 88 | - | - | - vs - | - | [f-build-r4.py](haiku-low-plan+luna-high-bare/f-build-r4.py) |
| haiku-low-plan+luna-high-bare | f-build | 5 | pass |  | 73 | 81 | - | - | - vs - | - | [f-build-r5.py](haiku-low-plan+luna-high-bare/f-build-r5.py) |
| haiku-low-plan+luna-low | f-build | 1 | pass |  | 83 | 92 | - | - | - vs - | - | [f-build-r1.py](haiku-low-plan+luna-low/f-build-r1.py) |
| haiku-low-plan+luna-low | f-build | 2 | pass |  | 74 | 86 | - | - | - vs - | - | [f-build-r2.py](haiku-low-plan+luna-low/f-build-r2.py) |
| haiku-low-plan+luna-low | f-build | 3 | pass |  | 76 | 88 | - | - | - vs - | - | [f-build-r3.py](haiku-low-plan+luna-low/f-build-r3.py) |
| haiku-low-plan+luna-low | f-build | 4 | pass |  | 82 | 95 | - | - | - vs - | - | [f-build-r4.py](haiku-low-plan+luna-low/f-build-r4.py) |
| haiku-low-plan+luna-low | f-build | 5 | pass |  | 80 | 87 | - | - | - vs - | - | [f-build-r5.py](haiku-low-plan+luna-low/f-build-r5.py) |
| haiku-medium | main | 1 | pass |  | 89 | 102 | 26 | 0 | -0.03 vs 0.03 | 0.68 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 84 | 101 | 8 | 0 | -0.29 vs 0.03 | 0.74 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 76 | 85 | 30 | 0 | 0.97 vs 0.03 | 1.06 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 82 | 99 | 8 | 0 | 0.16 vs 0.03 | 0.74 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 68 | 76 | 25 | 0 | -0.02 vs 0.03 | 1.06 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 68 | 79 | 18 | 0 | -0.17 vs 0.03 | 0.76 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 73 | 86 | 21 | 0 | 0.03 vs 0.03 | 0.77 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 81 | 91 | 25 | 0 | 0.02 vs 0.03 | 0.73 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 79 | 95 | 24 | 0 | -0.08 vs 0.03 | 0.75 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 63 | 77 | 22 | 0 | 0.04 vs 0.03 | 0.70 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-high-bare+haiku-on-fail | g-build | 1 | cached |  | 72 | 81 | - | - | - vs - | - | [g-build-r1.py](luna-high-bare+haiku-on-fail/g-build-r1.py) |
| luna-high-bare+haiku-on-fail | g-build | 2 | cached |  | 69 | 83 | - | - | - vs - | - | [g-build-r2.py](luna-high-bare+haiku-on-fail/g-build-r2.py) |
| luna-high-bare+haiku-on-fail | g-build | 3 | cached |  | 67 | 79 | - | - | - vs - | - | [g-build-r3.py](luna-high-bare+haiku-on-fail/g-build-r3.py) |
| luna-high-bare+haiku-on-fail | g-build | 4 | cached |  | 73 | 83 | - | - | - vs - | - | [g-build-r4.py](luna-high-bare+haiku-on-fail/g-build-r4.py) |
| luna-high-bare+haiku-on-fail | g-build | 5 | cached |  | 71 | 79 | - | - | - vs - | - | [g-build-r5.py](luna-high-bare+haiku-on-fail/g-build-r5.py) |
| luna-high-bare+haiku-review-all | g-repair | 1 | pass |  | 72 | 81 | - | - | - vs - | - | [g-repair-r1.py](luna-high-bare+haiku-review-all/g-repair-r1.py) |
| luna-high-bare+haiku-review-all | g-repair | 2 | pass |  | 69 | 83 | - | - | - vs - | - | [g-repair-r2.py](luna-high-bare+haiku-review-all/g-repair-r2.py) |
| luna-high-bare+haiku-review-all | g-repair | 3 | pass |  | 67 | 79 | - | - | - vs - | - | [g-repair-r3.py](luna-high-bare+haiku-review-all/g-repair-r3.py) |
| luna-high-bare+haiku-review-all | g-repair | 4 | pass |  | 73 | 83 | - | - | - vs - | - | [g-repair-r4.py](luna-high-bare+haiku-review-all/g-repair-r4.py) |
| luna-high-bare+haiku-review-all | g-repair | 5 | pass |  | 71 | 79 | - | - | - vs - | - | [g-repair-r5.py](luna-high-bare+haiku-review-all/g-repair-r5.py) |
| luna-low | main | 1 | pass |  | 80 | 92 | 28 | 0 | 0.99 vs 0.03 | 0.72 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 80 | 88 | 24 | 0 | 1.07 vs 0.03 | 1.14 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 72 | 82 | 26 | 0 | 1.08 vs 0.03 | 0.72 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | wrong | small case 2 | 72 | 84 | 21 | 0 | - vs - | - | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 76 | 84 | 24 | 0 | -0.14 vs 0.03 | 1.08 | [main-r5.py](luna-low/main-r5.py) |
| luna-low+haiku-on-fail | g-build | 1 | cached |  | 77 | 84 | - | - | - vs - | - | [g-build-r1.py](luna-low+haiku-on-fail/g-build-r1.py) |
| luna-low+haiku-on-fail | g-build | 2 | cached |  | 85 | 93 | - | - | - vs - | - | [g-build-r2.py](luna-low+haiku-on-fail/g-build-r2.py) |
| luna-low+haiku-on-fail | g-build | 3 | cached |  | 73 | 81 | - | - | - vs - | - | [g-build-r3.py](luna-low+haiku-on-fail/g-build-r3.py) |
| luna-low+haiku-on-fail | g-build | 4 | cached |  | 69 | 81 | - | - | - vs - | - | [g-build-r4.py](luna-low+haiku-on-fail/g-build-r4.py) |
| luna-low+haiku-on-fail | g-build | 5 | cached |  | 76 | 92 | - | - | - vs - | - | [g-build-r5.py](luna-low+haiku-on-fail/g-build-r5.py) |
| luna-low+haiku-review-all | g-repair | 1 | pass |  | 77 | 84 | - | - | - vs - | - | [g-repair-r1.py](luna-low+haiku-review-all/g-repair-r1.py) |
| luna-low+haiku-review-all | g-repair | 2 | pass |  | 85 | 93 | - | - | - vs - | - | [g-repair-r2.py](luna-low+haiku-review-all/g-repair-r2.py) |
| luna-low+haiku-review-all | g-repair | 3 | pass |  | 81 | 91 | - | - | - vs - | - | [g-repair-r3.py](luna-low+haiku-review-all/g-repair-r3.py) |
| luna-low+haiku-review-all | g-repair | 4 | pass |  | 69 | 81 | - | - | - vs - | - | [g-repair-r4.py](luna-low+haiku-review-all/g-repair-r4.py) |
| luna-low+haiku-review-all | g-repair | 5 | pass |  | 76 | 92 | - | - | - vs - | - | [g-repair-r5.py](luna-low+haiku-review-all/g-repair-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 73 | 86 | 18 | 0 | 0.03 vs 0.03 | 0.76 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | timeout | small cases: timeout | 79 | 90 | 25 | 0 | - vs - | - | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 72 | 80 | 19 | 0 | 0.04 vs 0.03 | 0.76 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 80 | 88 | 26 | 0 | 0.91 vs 0.03 | 1.14 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 72 | 80 | 21 | 0 | 0.92 vs 0.03 | 1.08 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 88 | 104 | 21 | 0 | -0.14 vs 0.03 | 0.73 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 68 | 82 | 19 | 0 | -0.27 vs 0.03 | 0.76 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 76 | 84 | 24 | 0 | 0.95 vs 0.03 | 1.12 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 78 | 89 | 14 | 0 | -0.08 vs 0.03 | 1.08 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 70 | 78 | 24 | 0 | 1.03 vs 0.03 | 1.07 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 61 | 73 | 22 | 0 | -0.04 vs 0.03 | 0.72 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 61 | 70 | 21 | 0 | -0.01 vs 0.03 | 0.72 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 66 | 79 | 22 | 0 | 0.18 vs 0.03 | 0.72 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 60 | 73 | 20 | 0 | 0.07 vs 0.03 | 0.72 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 58 | 72 | 23 | 0 | -0.06 vs 0.03 | 0.72 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 61 | 74 | 19 | 0 | 0.24 vs 0.03 | 0.72 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 69 | 76 | 24 | 0 | -0.03 vs 0.03 | 0.70 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 70 | 77 | 25 | 0 | -0.00 vs 0.03 | 0.70 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 74 | 81 | 24 | 0 | 0.11 vs 0.03 | 0.71 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 71 | 78 | 24 | 0 | -0.13 vs 0.03 | 0.71 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 66 | 73 | 23 | 0 | -0.03 vs 0.03 | 0.71 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 68 | 75 | 24 | 0 | 0.04 vs 0.03 | 0.70 | [main-r5.py](sonnet-medium/main-r5.py) |
