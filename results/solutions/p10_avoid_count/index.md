# p10_avoid_count

Rung L5. Signature: `def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 63 | 78 | 24 | 1 | 2.24 vs 2.24 | 1.26 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 63 | 79 | 21 | 0 | 2.39 vs 2.24 | 1.28 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 72 | 89 | 22 | 0 | 2.32 vs 2.24 | 1.36 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 64 | 80 | 21 | 1 | 2.54 vs 2.24 | 1.28 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 68 | 81 | 20 | 0 | 2.45 vs 2.24 | 1.42 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 64 | 79 | 22 | 0 | 2.60 vs 2.24 | 1.34 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 73 | 87 | 20 | 0 | 2.30 vs 2.24 | 1.13 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 80 | 93 | 21 | 1 | 2.34 vs 2.24 | 0.95 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 70 | 86 | 22 | 0 | 2.54 vs 2.24 | 1.02 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 82 | 97 | 21 | 0 | 2.63 vs 2.24 | 1.00 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 81 | 98 | 19 | 0 | 2.47 vs 2.24 | 1.07 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | pass |  | 72 | 85 | 24 | 0 | 2.50 vs 2.24 | 0.93 | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | crash | small case 0: NameError: name 'fail_links' is not defined | 63 | 77 | 17 | 6 | - vs - | - | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 71 | 83 | 23 | 0 | 2.21 vs 2.24 | 1.02 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 70 | 82 | 30 | 0 | 2.81 vs 2.24 | 1.04 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 72 | 87 | 19 | 0 | 2.63 vs 2.24 | 0.91 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-low | main | 1 | pass |  | 72 | 86 | 27 | 0 | 2.51 vs 2.24 | 1.27 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 90 | 104 | 25 | 0 | 2.77 vs 2.24 | 1.09 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 72 | 87 | 31 | 1 | 2.47 vs 2.24 | 1.36 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 76 | 90 | 23 | 1 | 2.41 vs 2.24 | 0.86 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 86 | 101 | 31 | 2 | 2.47 vs 2.24 | 1.05 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 76 | 91 | 25 | 0 | 2.74 vs 2.24 | 0.96 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | wrong | small case 121 | 74 | 88 | 25 | 0 | - vs - | - | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 79 | 93 | 25 | 1 | 2.55 vs 2.24 | 0.86 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 73 | 86 | 23 | 0 | 2.72 vs 2.24 | 0.91 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 81 | 96 | 23 | 1 | 2.60 vs 2.24 | 0.99 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 81 | 98 | 33 | 1 | 2.73 vs 2.24 | 0.95 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 77 | 92 | 28 | 0 | 2.71 vs 2.24 | 0.92 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 74 | 85 | 23 | 0 | 2.61 vs 2.24 | 1.03 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 84 | 100 | 23 | 1 | 2.68 vs 2.24 | 1.06 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 80 | 94 | 26 | 1 | 2.46 vs 2.24 | 0.93 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 75 | 86 | 27 | 0 | 2.25 vs 2.24 | 1.04 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 78 | 90 | 29 | 0 | 2.28 vs 2.24 | 1.06 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 75 | 86 | 26 | 0 | 2.47 vs 2.24 | 1.01 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 76 | 90 | 27 | 0 | 2.13 vs 2.24 | 1.04 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 77 | 89 | 27 | 0 | 2.54 vs 2.24 | 0.97 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 77 | 91 | 27 | 0 | 2.49 vs 2.24 | 1.05 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 79 | 84 | 28 | 0 | 2.54 vs 2.24 | 1.08 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 82 | 87 | 27 | 1 | 2.43 vs 2.24 | 1.12 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 84 | 92 | 20 | 0 | 2.10 vs 2.24 | 0.96 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 76 | 85 | 28 | 0 | 2.46 vs 2.24 | 1.03 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 79 | 81 | 24 | 0 | 2.38 vs 2.24 | 1.05 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 72 | 78 | 27 | 1 | 2.55 vs 2.24 | 1.23 | [main-r5.py](sonnet-medium/main-r5.py) |
