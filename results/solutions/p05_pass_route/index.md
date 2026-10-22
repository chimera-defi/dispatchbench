# p05_pass_route

Rung L3. Signature: `def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | calibration | 0 | pass |  | 36 | 46 | 16 | 0 | 1.49 vs 1.24 | 0.96 | [calibration-r0.py](haiku-low/calibration-r0.py) |
| haiku-low | main | 1 | pass |  | 38 | 51 | 16 | 0 | 1.18 vs 1.24 | 1.66 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 38 | 49 | 17 | 0 | 1.23 vs 1.24 | 1.66 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 35 | 46 | 17 | 0 | 1.39 vs 1.24 | 1.42 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 38 | 51 | 16 | 0 | 1.18 vs 1.24 | 1.66 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 39 | 53 | 16 | 0 | 1.55 vs 1.24 | 0.98 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 37 | 51 | 16 | 0 | 1.36 vs 1.24 | 0.96 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 37 | 46 | 16 | 0 | 1.23 vs 1.24 | 1.42 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | wrong | small case 0 | 40 | 49 | 16 | 0 | - vs - | - | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 40 | 53 | 17 | 0 | 1.40 vs 1.24 | 0.94 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 40 | 53 | 15 | 0 | 1.44 vs 1.24 | 1.57 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | exploratory | 1 | wrong | small case 0 | 33 | 40 | 15 | 0 | - vs - | - | [exploratory-r1.py](luna-high/exploratory-r1.py) |
| luna-high | exploratory | 2 | pass |  | 40 | 48 | 14 | 0 | 1.26 vs 1.24 | 0.91 | [exploratory-r2.py](luna-high/exploratory-r2.py) |
| luna-high | exploratory | 3 | pass |  | 39 | 47 | 14 | 0 | 1.50 vs 1.24 | 0.96 | [exploratory-r3.py](luna-high/exploratory-r3.py) |
| luna-high | exploratory | 4 | pass |  | 36 | 43 | 16 | 0 | 1.30 vs 1.24 | 0.98 | [exploratory-r4.py](luna-high/exploratory-r4.py) |
| luna-high | exploratory | 5 | pass |  | 36 | 44 | 16 | 0 | 1.29 vs 1.24 | 1.02 | [exploratory-r5.py](luna-high/exploratory-r5.py) |
| luna-low | main | 1 | pass |  | 37 | 45 | 16 | 1 | 1.40 vs 1.24 | 0.98 | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 37 | 45 | 16 | 0 | 1.35 vs 1.24 | 1.00 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 37 | 45 | 16 | 0 | 1.27 vs 1.24 | 0.98 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 37 | 44 | 16 | 0 | 1.40 vs 1.24 | 1.02 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 36 | 43 | 16 | 0 | 1.35 vs 1.24 | 1.00 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 37 | 45 | 16 | 0 | 1.23 vs 1.24 | 1.02 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | pass |  | 37 | 46 | 16 | 0 | 1.25 vs 1.24 | 0.98 | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | pass |  | 37 | 45 | 16 | 0 | 1.23 vs 1.24 | 1.02 | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 35 | 43 | 16 | 0 | 1.47 vs 1.24 | 1.00 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | pass |  | 36 | 44 | 16 | 0 | 1.39 vs 1.24 | 1.00 | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 39 | 46 | 15 | 0 | 1.36 vs 1.24 | 0.96 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | pass |  | 36 | 44 | 16 | 0 | 1.24 vs 1.24 | 1.02 | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 41 | 49 | 15 | 0 | 1.26 vs 1.24 | 0.95 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | pass |  | 36 | 44 | 16 | 0 | 1.38 vs 1.24 | 1.02 | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | pass |  | 37 | 45 | 16 | 1 | 1.21 vs 1.24 | 0.98 | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | calibration | 0 | pass |  | 37 | 44 | 14 | 0 | 1.35 vs 1.24 | 0.96 | [calibration-r0.py](sol61-medium/calibration-r0.py) |
| sol61-medium | main | 1 | pass |  | 35 | 42 | 14 | 0 | 1.34 vs 1.24 | 0.97 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 35 | 42 | 14 | 0 | 1.26 vs 1.24 | 0.97 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 34 | 42 | 14 | 0 | 1.40 vs 1.24 | 0.89 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 34 | 41 | 14 | 0 | 1.28 vs 1.24 | 0.91 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 35 | 42 | 15 | 0 | 1.23 vs 1.24 | 0.91 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | calibration | 0 | pass |  | 36 | 38 | 15 | 0 | 1.58 vs 1.24 | 0.91 | [calibration-r0.py](sonnet-medium/calibration-r0.py) |
| sonnet-medium | main | 1 | pass |  | 36 | 38 | 15 | 0 | 1.48 vs 1.24 | 0.91 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 36 | 38 | 16 | 0 | 1.38 vs 1.24 | 0.98 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 36 | 38 | 15 | 0 | 1.49 vs 1.24 | 0.93 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 36 | 38 | 15 | 0 | 1.54 vs 1.24 | 0.91 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 37 | 39 | 15 | 0 | 1.62 vs 1.24 | 0.91 | [main-r5.py](sonnet-medium/main-r5.py) |
