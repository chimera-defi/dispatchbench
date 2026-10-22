# p11_best_average

Rung L6. Signature: `def best_average(a: list[int], k: int) -> list[int]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | main | 1 | pass |  | 29 | 37 | 9 | 0 | 1.06 vs 1.35 | 1.00 | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 29 | 39 | 9 | 0 | 1.22 vs 1.35 | 2.85 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 29 | 39 | 7 | 0 | 1.13 vs 1.35 | 1.18 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 30 | 42 | 10 | 1 | 1.14 vs 1.35 | 1.13 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 32 | 46 | 8 | 0 | 1.10 vs 1.35 | 1.00 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 32 | 40 | 8 | 0 | 1.07 vs 1.35 | 1.13 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 28 | 36 | 9 | 0 | 1.13 vs 1.35 | 1.00 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 29 | 34 | 8 | 0 | 1.29 vs 1.35 | 1.00 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 30 | 38 | 8 | 0 | 1.15 vs 1.35 | 1.13 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 31 | 41 | 8 | 0 | 1.08 vs 1.35 | 2.17 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | escalation | 1 | pass |  | 39 | 47 | 8 | 0 | 1.07 vs 1.35 | 1.02 | [escalation-r1.py](luna-high/escalation-r1.py) |
| luna-high | escalation | 2 | pass |  | 38 | 48 | 9 | 0 | 1.00 vs 1.35 | 1.00 | [escalation-r2.py](luna-high/escalation-r2.py) |
| luna-high | escalation | 3 | pass |  | 37 | 45 | 8 | 0 | 1.05 vs 1.35 | 1.00 | [escalation-r3.py](luna-high/escalation-r3.py) |
| luna-high | escalation | 4 | pass |  | 38 | 49 | 8 | 0 | 1.06 vs 1.35 | 1.00 | [escalation-r4.py](luna-high/escalation-r4.py) |
| luna-high | escalation | 5 | pass |  | 33 | 40 | 8 | 0 | 1.02 vs 1.35 | 1.00 | [escalation-r5.py](luna-high/escalation-r5.py) |
| luna-low | main | 1 | wrong | small case 0 | 35 | 47 | 8 | 0 | - vs - | - | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | pass |  | 37 | 49 | 9 | 0 | 1.05 vs 1.35 | 1.00 | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | pass |  | 34 | 44 | 8 | 1 | 1.03 vs 1.35 | 1.02 | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | pass |  | 35 | 44 | 8 | 0 | 1.01 vs 1.35 | 1.00 | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | pass |  | 30 | 41 | 8 | 0 | 0.99 vs 1.35 | 1.03 | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | pass |  | 34 | 42 | 8 | 1 | 1.02 vs 1.35 | 1.03 | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | wrong | small case 0 | 35 | 44 | 8 | 0 | - vs - | - | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | wrong | small case 0 | 33 | 43 | 8 | 1 | - vs - | - | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | pass |  | 34 | 44 | 8 | 0 | 1.06 vs 1.35 | 1.03 | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | crash | small case 0: IndexError: deque index out of range | 31 | 37 | 8 | 2 | - vs - | - | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | pass |  | 38 | 48 | 9 | 0 | 1.05 vs 1.35 | 1.03 | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | wrong | small case 6 | 36 | 46 | 8 | 0 | - vs - | - | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | pass |  | 39 | 48 | 9 | 0 | 1.09 vs 1.35 | 1.03 | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | wrong | small case 0 | 33 | 42 | 9 | 0 | - vs - | - | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | wrong | small case 6 | 32 | 43 | 8 | 0 | - vs - | - | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | main | 1 | pass |  | 37 | 47 | 8 | 0 | 1.12 vs 1.35 | 1.00 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | pass |  | 39 | 49 | 8 | 0 | 1.09 vs 1.35 | 1.00 | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 34 | 42 | 8 | 0 | 1.00 vs 1.35 | 1.00 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 38 | 46 | 8 | 0 | 1.06 vs 1.35 | 1.00 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | pass |  | 36 | 46 | 8 | 0 | 1.09 vs 1.35 | 1.02 | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | main | 1 | pass |  | 27 | 29 | 8 | 0 | 1.08 vs 1.35 | 1.00 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 28 | 29 | 8 | 0 | 1.42 vs 1.35 | 1.00 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 27 | 29 | 9 | 0 | 1.08 vs 1.35 | 1.00 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 26 | 29 | 7 | 0 | 1.10 vs 1.35 | 1.20 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 32 | 34 | 8 | 0 | 1.36 vs 1.35 | 1.00 | [main-r5.py](sonnet-medium/main-r5.py) |
