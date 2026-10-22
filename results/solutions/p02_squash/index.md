# p02_squash

Rung L1. Signature: `def squash(s: str) -> str:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 20 | 21 | 5 | 0 | 1.11 vs 1.10 | 1.00 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 21 | 23 | 5 | 0 | 1.07 vs 1.10 | 1.47 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 17 | 17 | 6 | 0 | 1.18 vs 1.10 | 1.00 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 20 | 22 | 5 | 0 | 1.15 vs 1.10 | 1.00 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 20 | 21 | 5 | 0 | 1.11 vs 1.10 | 1.00 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 20 | 21 | 5 | 0 | 0.95 vs 1.10 | 1.00 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 21 | 22 | 5 | 0 | 0.95 vs 1.10 | 1.47 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 12 | 15 | 4 | 0 | 1.20 vs 1.10 | 1.00 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 20 | 22 | 5 | 0 | 1.13 vs 1.10 | 1.00 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 20 | 21 | 5 | 0 | 0.90 vs 1.10 | 1.00 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 20 | 21 | 5 | 0 | 0.95 vs 1.10 | 1.00 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 18 | 23 | 7 | 0 | 0.87 vs 1.10 | 1.47 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 18 | 23 | 7 | 0 | 1.02 vs 1.10 | 1.47 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 18 | 23 | 7 | 0 | 1.15 vs 1.10 | 1.47 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 18 | 23 | 7 | 0 | 1.04 vs 1.10 | 1.47 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 16 | 20 | 5 | 0 | 1.11 vs 1.10 | 1.00 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-low | main | 1 | pass |  | 18 | 22 | 5 | 0 | 0.82 vs 1.10 | 1.47 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 18 | 23 | 7 | 0 | 1.05 vs 1.10 | 1.46 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 18 | 23 | 7 | 0 | 1.04 vs 1.10 | 1.47 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 18 | 23 | 7 | 0 | 1.06 vs 1.10 | 1.47 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 18 | 23 | 5 | 0 | 0.81 vs 1.10 | 1.46 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 20 | 26 | 9 | 0 | 1.11 vs 1.10 | 1.47 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | pass |  | 18 | 23 | 7 | 0 | 1.12 vs 1.10 | 1.47 | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 17 | 20 | 5 | 0 | 0.99 vs 1.10 | 1.46 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 19 | 23 | 6 | 0 | 1.09 vs 1.10 | 1.47 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 17 | 20 | 5 | 0 | 0.99 vs 1.10 | 1.46 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 19 | 24 | 5 | 0 | 0.95 vs 1.10 | 1.46 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 18 | 23 | 7 | 0 | 0.95 vs 1.10 | 1.47 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 18 | 23 | 7 | 0 | 0.87 vs 1.10 | 1.47 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 18 | 23 | 5 | 0 | 1.07 vs 1.10 | 1.46 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 21 | 27 | 6 | 0 | 1.34 vs 1.10 | 1.46 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 18 | 22 | 7 | 0 | 0.96 vs 1.10 | 1.47 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 18 | 23 | 7 | 0 | 1.15 vs 1.10 | 1.47 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 18 | 22 | 7 | 0 | 0.96 vs 1.10 | 1.47 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 18 | 23 | 7 | 0 | 0.81 vs 1.10 | 1.47 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 18 | 22 | 7 | 0 | 1.05 vs 1.10 | 1.47 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 18 | 23 | 7 | 0 | 1.14 vs 1.10 | 1.47 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 20 | 21 | 5 | 0 | 1.28 vs 1.10 | 1.47 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 20 | 21 | 5 | 0 | 1.28 vs 1.10 | 1.47 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 20 | 21 | 5 | 0 | 1.04 vs 1.10 | 1.47 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 18 | 18 | 8 | 0 | 1.00 vs 1.10 | 1.47 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 20 | 21 | 5 | 0 | 1.11 vs 1.10 | 1.47 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 20 | 21 | 5 | 0 | 1.11 vs 1.10 | 1.47 | [main-r5.py](sonnet-medium/main-r5.py) |
