# p07_weighted_distance_sums

Rung L4. Signature: `def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 38 | 49 | 13 | 0 | 1.18 vs 1.24 | 0.96 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 34 | 45 | 11 | 0 | 1.21 vs 1.24 | 0.96 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 34 | 46 | 11 | 0 | 1.19 vs 1.24 | 0.96 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 34 | 45 | 10 | 0 | 1.19 vs 1.24 | 0.96 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 34 | 46 | 10 | 0 | 1.19 vs 1.24 | 0.96 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 38 | 50 | 14 | 0 | 1.25 vs 1.24 | 0.96 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 34 | 47 | 12 | 0 | 1.21 vs 1.24 | 0.89 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 34 | 46 | 11 | 0 | 1.20 vs 1.24 | 0.96 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 34 | 45 | 10 | 0 | 1.22 vs 1.24 | 0.96 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 33 | 45 | 10 | 0 | 1.20 vs 1.24 | 0.94 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 34 | 47 | 10 | 0 | 1.23 vs 1.24 | 0.96 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 26 | 32 | 9 | 0 | 1.22 vs 1.24 | 0.89 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 25 | 31 | 9 | 0 | 1.23 vs 1.24 | 0.89 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 26 | 33 | 9 | 0 | 1.24 vs 1.24 | 0.89 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 25 | 31 | 9 | 0 | 1.28 vs 1.24 | 0.89 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 25 | 31 | 9 | 0 | 1.18 vs 1.24 | 0.89 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-low | main | 1 | pass |  | 23 | 29 | 9 | 0 | 1.31 vs 1.24 | 0.85 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 23 | 29 | 9 | 0 | 1.23 vs 1.24 | 0.85 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 23 | 31 | 9 | 0 | 1.25 vs 1.24 | 0.85 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 27 | 35 | 12 | 0 | 1.25 vs 1.24 | 0.89 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 23 | 29 | 9 | 0 | 1.24 vs 1.24 | 0.85 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 30 | 39 | 11 | 0 | 1.29 vs 1.24 | 0.89 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | pass |  | 33 | 43 | 11 | 0 | 1.19 vs 1.24 | 0.89 | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 23 | 29 | 9 | 0 | 1.23 vs 1.24 | 0.85 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 23 | 29 | 9 | 0 | 1.32 vs 1.24 | 0.85 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 23 | 29 | 9 | 0 | 1.28 vs 1.24 | 0.85 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 26 | 33 | 8 | 0 | 1.22 vs 1.24 | 0.96 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 23 | 29 | 9 | 0 | 1.24 vs 1.24 | 0.85 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 23 | 29 | 9 | 0 | 1.27 vs 1.24 | 0.85 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 26 | 34 | 10 | 0 | 1.21 vs 1.24 | 0.89 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 23 | 29 | 9 | 0 | 1.28 vs 1.24 | 0.85 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 27 | 31 | 10 | 0 | 1.26 vs 1.24 | 0.81 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 28 | 35 | 10 | 0 | 1.26 vs 1.24 | 0.81 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 25 | 30 | 8 | 0 | 1.26 vs 1.24 | 0.81 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 26 | 33 | 8 | 0 | 1.24 vs 1.24 | 0.81 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 25 | 30 | 8 | 0 | 1.26 vs 1.24 | 0.81 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 26 | 33 | 8 | 0 | 1.16 vs 1.24 | 0.81 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 33 | 36 | 10 | 0 | 1.14 vs 1.24 | 0.96 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 36 | 43 | 13 | 0 | 1.25 vs 1.24 | 0.89 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 33 | 36 | 11 | 0 | 1.20 vs 1.24 | 0.89 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 33 | 37 | 10 | 0 | 1.19 vs 1.24 | 0.96 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 33 | 37 | 10 | 0 | 1.21 vs 1.24 | 0.96 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 33 | 36 | 11 | 0 | 1.20 vs 1.24 | 0.89 | [main-r5.py](sonnet-medium/main-r5.py) |
