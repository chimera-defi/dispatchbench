# p01_overlap_minutes

Rung L1. Signature: `def overlap_minutes(meetings: list[list[int]], k: int) -> int:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 16 | 17 | 5 | 0 | 1.14 vs 1.15 | 2.00 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 17 | 20 | 5 | 0 | 1.29 vs 1.15 | 1.16 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 16 | 17 | 5 | 0 | 1.32 vs 1.15 | 1.00 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 16 | 17 | 6 | 0 | 1.04 vs 1.15 | 2.00 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 16 | 19 | 5 | 0 | 1.17 vs 1.15 | 2.00 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 16 | 18 | 5 | 0 | 1.14 vs 1.15 | 2.00 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 16 | 17 | 6 | 0 | 1.06 vs 1.15 | 1.16 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 15 | 16 | 6 | 0 | 1.16 vs 1.15 | 1.16 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 21 | 22 | 8 | 0 | 1.17 vs 1.15 | 1.00 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 16 | 17 | 6 | 0 | 1.30 vs 1.15 | 1.16 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 15 | 16 | 6 | 0 | 1.17 vs 1.15 | 1.16 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 20 | 25 | 7 | 0 | 1.13 vs 1.15 | 1.00 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 22 | 27 | 7 | 0 | 1.17 vs 1.15 | 1.00 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 22 | 28 | 7 | 0 | 1.18 vs 1.15 | 1.00 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 20 | 24 | 8 | 0 | 1.16 vs 1.15 | 1.00 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 20 | 25 | 8 | 0 | 1.11 vs 1.15 | 1.00 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-low | main | 1 | pass |  | 20 | 26 | 8 | 0 | 1.18 vs 1.15 | 1.00 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 20 | 26 | 8 | 0 | 1.37 vs 1.15 | 1.00 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 20 | 26 | 8 | 0 | 1.33 vs 1.15 | 1.00 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 20 | 26 | 8 | 0 | 1.37 vs 1.15 | 1.00 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 20 | 25 | 8 | 0 | 1.24 vs 1.15 | 1.00 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 22 | 27 | 8 | 0 | 1.05 vs 1.15 | 1.00 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | pass |  | 20 | 25 | 8 | 0 | 1.16 vs 1.15 | 1.00 | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 22 | 28 | 8 | 0 | 1.19 vs 1.15 | 1.00 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 22 | 27 | 8 | 0 | 1.05 vs 1.15 | 1.00 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 22 | 26 | 8 | 0 | 1.20 vs 1.15 | 1.00 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 22 | 28 | 8 | 0 | 1.14 vs 1.15 | 1.00 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 20 | 26 | 8 | 0 | 1.21 vs 1.15 | 1.00 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 20 | 26 | 8 | 0 | 1.37 vs 1.15 | 1.00 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 20 | 26 | 8 | 0 | 1.37 vs 1.15 | 1.00 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 20 | 26 | 8 | 0 | 1.09 vs 1.15 | 1.00 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 17 | 21 | 6 | 0 | 1.23 vs 1.15 | 1.16 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 17 | 21 | 6 | 0 | 1.23 vs 1.15 | 1.16 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 17 | 21 | 6 | 0 | 1.23 vs 1.15 | 1.16 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 15 | 18 | 5 | 0 | 1.19 vs 1.15 | 1.16 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 17 | 21 | 6 | 0 | 1.06 vs 1.15 | 1.16 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 17 | 21 | 6 | 0 | 1.06 vs 1.15 | 1.16 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 16 | 16 | 5 | 0 | 1.37 vs 1.15 | 1.00 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 16 | 16 | 5 | 0 | 1.37 vs 1.15 | 1.00 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 16 | 16 | 5 | 0 | 1.37 vs 1.15 | 1.00 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 16 | 16 | 5 | 0 | 1.37 vs 1.15 | 1.00 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 16 | 16 | 5 | 0 | 1.11 vs 1.15 | 1.16 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 16 | 16 | 5 | 0 | 1.37 vs 1.15 | 1.00 | [main-r5.py](sonnet-medium/main-r5.py) |
