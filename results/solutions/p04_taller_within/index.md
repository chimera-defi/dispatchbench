# p04_taller_within

Rung L2. Signature: `def taller_within(a: list[int], k: int) -> list[int]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 27 | 32 | 5 | 0 | 1.13 vs 1.04 | 1.00 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 27 | 33 | 5 | 0 | 1.08 vs 1.04 | 1.00 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 29 | 35 | 5 | 0 | 1.07 vs 1.04 | 1.00 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 27 | 30 | 4 | 0 | 1.11 vs 1.04 | 1.00 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 28 | 34 | 5 | 0 | 1.15 vs 1.04 | 1.00 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 35 | 45 | 6 | 0 | 1.14 vs 1.04 | 1.03 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 27 | 33 | 5 | 0 | 1.17 vs 1.04 | 1.00 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 26 | 31 | 5 | 0 | 1.18 vs 1.04 | 1.00 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 28 | 35 | 5 | 1 | 1.15 vs 1.04 | 1.00 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 28 | 33 | 5 | 0 | 1.23 vs 1.04 | 1.00 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 29 | 35 | 5 | 0 | 1.24 vs 1.04 | 0.68 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | escalation | 1 | pass |  | 25 | 31 | 4 | 0 | 1.04 vs 1.04 | 1.00 | [escalation-r1.py](luna-high/escalation-r1.py) |
| luna-high | escalation | 2 | pass |  | 25 | 32 | 5 | 0 | 1.06 vs 1.04 | 1.00 | [escalation-r2.py](luna-high/escalation-r2.py) |
| luna-high | escalation | 3 | pass |  | 27 | 35 | 5 | 0 | 1.07 vs 1.04 | 1.00 | [escalation-r3.py](luna-high/escalation-r3.py) |
| luna-high | escalation | 4 | pass |  | 23 | 28 | 4 | 0 | 1.19 vs 1.04 | 1.00 | [escalation-r4.py](luna-high/escalation-r4.py) |
| luna-high | escalation | 5 | pass |  | 28 | 35 | 5 | 0 | 1.31 vs 1.04 | 1.00 | [escalation-r5.py](luna-high/escalation-r5.py) |
| luna-low | main | 1 | pass |  | 27 | 37 | 5 | 0 | 1.03 vs 1.04 | 1.00 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | timeout | large case 0: timeout | 12 | 16 | 7 | 0 | - vs - | - | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | timeout | large case 0: timeout | 16 | 22 | 8 | 0 | - vs - | - | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | wrong | small case 0 | 25 | 31 | 5 | 0 | - vs - | - | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | wrong | small case 10 | 13 | 18 | 10 | 0 | - vs - | - | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | wrong | small case 0 | 26 | 33 | 4 | 0 | - vs - | - | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | wrong | small case 0 | 23 | 30 | 5 | 0 | - vs - | - | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | wrong | small case 0 | 24 | 30 | 5 | 0 | - vs - | - | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | wrong | small case 0 | 24 | 30 | 5 | 0 | - vs - | - | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 28 | 36 | 5 | 1 | 1.33 vs 1.04 | 1.00 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | wrong | small case 0 | 24 | 30 | 5 | 0 | - vs - | - | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | timeout | large case 0: timeout | 10 | 13 | 6 | 0 | - vs - | - | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | wrong | small case 0 | 24 | 30 | 5 | 0 | - vs - | - | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | wrong | small case 0 | 24 | 31 | 5 | 0 | - vs - | - | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 25 | 33 | 5 | 0 | 1.23 vs 1.04 | 1.00 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 25 | 32 | 8 | 0 | 1.13 vs 1.04 | 0.94 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 26 | 33 | 8 | 0 | 1.01 vs 1.04 | 0.94 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 26 | 33 | 8 | 0 | 1.17 vs 1.04 | 0.94 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 26 | 32 | 9 | 0 | 1.13 vs 1.04 | 1.00 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 26 | 32 | 8 | 0 | 1.17 vs 1.04 | 0.94 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 26 | 32 | 8 | 0 | 1.18 vs 1.04 | 0.94 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 25 | 28 | 5 | 0 | 1.20 vs 1.04 | 1.06 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 28 | 31 | 5 | 0 | 1.14 vs 1.04 | 1.06 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 29 | 33 | 7 | 0 | 1.44 vs 1.04 | 1.06 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 28 | 32 | 6 | 0 | 1.15 vs 1.04 | 0.68 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 28 | 33 | 4 | 0 | 1.08 vs 1.04 | 0.68 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 29 | 35 | 6 | 0 | 1.09 vs 1.04 | 0.68 | [main-r5.py](sonnet-medium/main-r5.py) |
