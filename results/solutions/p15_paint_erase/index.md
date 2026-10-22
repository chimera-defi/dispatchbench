# p15_paint_erase

Rung L7. Signature: `def paint(n: int, ops: list[list[int]]) -> list[list[int]]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | hard | 1 | pass |  | 81 | 94 | 7 | 4 | 1.08 vs 0.93 | 0.82 | [hard-r1.py](haiku-low/hard-r1.py) |
| haiku-low | hard | 2 | timeout | large case 1: timeout | 58 | 71 | 17 | 4 | - vs - | - | [hard-r2.py](haiku-low/hard-r2.py) |
| haiku-low | hard | 3 | timeout | large case 1: timeout | 44 | 59 | 16 | 2 | - vs - | - | [hard-r3.py](haiku-low/hard-r3.py) |
| haiku-low | hard | 4 | timeout | large case 1: timeout | 51 | 68 | 21 | 2 | - vs - | - | [hard-r4.py](haiku-low/hard-r4.py) |
| haiku-low | hard | 5 | pass |  | 63 | 78 | 7 | 4 | 1.03 vs 0.93 | 0.61 | [hard-r5.py](haiku-low/hard-r5.py) |
| luna-high | hard | 1 | pass |  | 100 | 113 | 12 | 0 | 1.01 vs 0.93 | 1.00 | [hard-r1.py](luna-high/hard-r1.py) |
| luna-high | hard | 2 | pass |  | 106 | 126 | 8 | 0 | 1.06 vs 0.93 | 1.14 | [hard-r2.py](luna-high/hard-r2.py) |
| luna-high | hard | 3 | pass |  | 86 | 100 | 10 | 0 | 1.25 vs 0.93 | 0.91 | [hard-r3.py](luna-high/hard-r3.py) |
| luna-high | hard | 4 | pass |  | 115 | 133 | 8 | 0 | 1.12 vs 0.93 | 1.02 | [hard-r4.py](luna-high/hard-r4.py) |
| luna-high | hard | 5 | pass |  | 66 | 74 | 8 | 0 | 1.11 vs 0.93 | 0.61 | [hard-r5.py](luna-high/hard-r5.py) |
| sol61-medium | hard | 1 | pass |  | 37 | 48 | 12 | 0 | 1.19 vs 0.93 | 0.86 | [hard-r1.py](sol61-medium/hard-r1.py) |
| sol61-medium | hard | 2 | pass |  | 67 | 80 | 11 | 0 | 1.04 vs 0.93 | 0.61 | [hard-r2.py](sol61-medium/hard-r2.py) |
| sol61-medium | hard | 3 | pass |  | 67 | 82 | 7 | 0 | 1.04 vs 0.93 | 0.76 | [hard-r3.py](sol61-medium/hard-r3.py) |
| sol61-medium | hard | 4 | pass |  | 40 | 53 | 13 | 1 | 0.98 vs 0.93 | 0.84 | [hard-r4.py](sol61-medium/hard-r4.py) |
| sol61-medium | hard | 5 | pass |  | 54 | 67 | 14 | 0 | 0.99 vs 0.93 | 0.90 | [hard-r5.py](sol61-medium/hard-r5.py) |
| sonnet-medium | hard | 1 | pass |  | 57 | 62 | 13 | 2 | 1.07 vs 0.93 | 0.68 | [hard-r1.py](sonnet-medium/hard-r1.py) |
| sonnet-medium | hard | 2 | pass |  | 62 | 70 | 6 | 1 | 1.11 vs 0.93 | 0.76 | [hard-r2.py](sonnet-medium/hard-r2.py) |
| sonnet-medium | hard | 3 | pass |  | 58 | 64 | 10 | 2 | 1.06 vs 0.93 | 0.61 | [hard-r3.py](sonnet-medium/hard-r3.py) |
| sonnet-medium | hard | 4 | pass |  | 58 | 62 | 10 | 1 | 1.10 vs 0.93 | 0.88 | [hard-r4.py](sonnet-medium/hard-r4.py) |
| sonnet-medium | hard | 5 | pass |  | 63 | 68 | 17 | 3 | 1.11 vs 0.93 | 0.68 | [hard-r5.py](sonnet-medium/hard-r5.py) |
