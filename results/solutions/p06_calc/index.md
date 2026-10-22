# p06_calc

Rung L3. Signature: `def calc(expr: str) -> int | str:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 101 | 117 | 9 | 0 | 0.93 vs 1.11 | 1.08 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 80 | 93 | 7 | 0 | 1.21 vs 1.11 | 1.00 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 76 | 85 | 6 | 0 | 0.96 vs 1.11 | 0.39 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 83 | 97 | 7 | 0 | 1.27 vs 1.11 | 1.02 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 74 | 83 | 5 | 0 | 1.17 vs 1.11 | 0.39 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 70 | 78 | 7 | 0 | 1.05 vs 1.11 | 0.38 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 84 | 97 | 6 | 0 | 1.20 vs 1.11 | 1.68 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 84 | 97 | 7 | 0 | 1.22 vs 1.11 | 1.61 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 89 | 102 | 8 | 0 | 0.97 vs 1.11 | 1.02 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 72 | 82 | 5 | 0 | 1.21 vs 1.11 | 0.39 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 101 | 117 | 8 | 0 | 1.30 vs 1.11 | 1.61 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 88 | 102 | 9 | 0 | 1.09 vs 1.11 | 1.00 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 89 | 102 | 20 | 0 | 0.98 vs 1.11 | 0.10 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 88 | 103 | 9 | 0 | 0.87 vs 1.11 | 0.07 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 92 | 105 | 3 | 0 | 1.05 vs 1.11 | 0.34 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 79 | 96 | 10 | 0 | 0.74 vs 1.11 | 0.13 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-low | main | 1 | pass |  | 79 | 87 | 9 | 0 | 1.01 vs 1.11 | 0.98 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 78 | 89 | 7 | 0 | 1.13 vs 1.11 | 0.99 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 77 | 87 | 7 | 0 | 1.10 vs 1.11 | 0.13 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 76 | 84 | 8 | 0 | 0.99 vs 1.11 | 0.98 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 77 | 85 | 7 | 0 | 0.99 vs 1.11 | 0.98 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 77 | 85 | 9 | 0 | 0.96 vs 1.11 | 0.98 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | pass |  | 76 | 85 | 7 | 0 | 1.00 vs 1.11 | 0.99 | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 76 | 85 | 7 | 0 | 1.21 vs 1.11 | 0.99 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 76 | 87 | 7 | 0 | 0.98 vs 1.11 | 0.99 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 76 | 85 | 7 | 0 | 0.84 vs 1.11 | 0.99 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 79 | 87 | 9 | 0 | 1.02 vs 1.11 | 0.98 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 77 | 85 | 8 | 0 | 1.18 vs 1.11 | 0.98 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 77 | 94 | 8 | 0 | 1.20 vs 1.11 | 0.19 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 77 | 85 | 7 | 0 | 1.16 vs 1.11 | 0.98 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 79 | 87 | 9 | 0 | 0.87 vs 1.11 | 0.98 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 71 | 85 | 20 | 0 | 0.98 vs 1.11 | 0.08 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 72 | 85 | 18 | 0 | 0.90 vs 1.11 | 0.08 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 71 | 84 | 20 | 0 | 0.61 vs 1.11 | 0.08 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 71 | 84 | 20 | 0 | 1.15 vs 1.11 | 0.08 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 70 | 82 | 18 | 0 | 1.15 vs 1.11 | 0.08 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 71 | 85 | 18 | 0 | 1.33 vs 1.11 | 0.08 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 81 | 91 | 7 | 0 | 0.94 vs 1.11 | 0.40 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 86 | 96 | 7 | 0 | 1.10 vs 1.11 | 0.21 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 91 | 99 | 8 | 0 | 1.04 vs 1.11 | 1.05 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 91 | 100 | 8 | 0 | 1.19 vs 1.11 | 0.20 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 85 | 95 | 7 | 0 | 1.23 vs 1.11 | 0.21 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 76 | 84 | 7 | 0 | 1.18 vs 1.11 | 0.38 | [main-r5.py](sonnet-medium/main-r5.py) |
