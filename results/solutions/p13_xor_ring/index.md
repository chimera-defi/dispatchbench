# p13_xor_ring

Rung L7. Signature: `def evolve(state: str, offsets: list[int], t: int) -> str:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | hard | 1 | pass |  | 29 | 40 | 9 | 0 | 1.21 vs 0.77 | 1.05 | [hard-r1.py](haiku-low/hard-r1.py) |
| haiku-low | hard | 2 | pass |  | 23 | 33 | 12 | 1 | 0.84 vs 0.77 | 6.62 | [hard-r2.py](haiku-low/hard-r2.py) |
| haiku-low | hard | 3 | pass |  | 29 | 41 | 10 | 0 | 0.99 vs 0.77 | 6.41 | [hard-r3.py](haiku-low/hard-r3.py) |
| haiku-low | hard | 4 | pass |  | 29 | 40 | 9 | 0 | 0.70 vs 0.77 | 1.05 | [hard-r4.py](haiku-low/hard-r4.py) |
| haiku-low | hard | 5 | pass |  | 35 | 47 | 11 | 0 | 0.52 vs 0.77 | 1.06 | [hard-r5.py](haiku-low/hard-r5.py) |
| luna-high | hard | 1 | pass |  | 33 | 39 | 6 | 0 | 0.41 vs 0.77 | 0.30 | [hard-r1.py](luna-high/hard-r1.py) |
| luna-high | hard | 2 | pass |  | 32 | 39 | 9 | 0 | 0.89 vs 0.77 | 1.02 | [hard-r2.py](luna-high/hard-r2.py) |
| luna-high | hard | 3 | pass |  | 43 | 50 | 11 | 0 | 1.07 vs 0.77 | 1.04 | [hard-r3.py](luna-high/hard-r3.py) |
| luna-high | hard | 4 | pass |  | 35 | 45 | 9 | 0 | 0.90 vs 0.77 | 1.05 | [hard-r4.py](luna-high/hard-r4.py) |
| luna-high | hard | 5 | pass |  | 18 | 21 | 10 | 0 | 0.91 vs 0.77 | 1.02 | [hard-r5.py](luna-high/hard-r5.py) |
| sol61-medium | hard | 1 | pass |  | 17 | 23 | 8 | 0 | 0.31 vs 0.77 | 0.27 | [hard-r1.py](sol61-medium/hard-r1.py) |
| sol61-medium | hard | 2 | pass |  | 32 | 39 | 14 | 0 | 0.15 vs 0.77 | 0.30 | [hard-r2.py](sol61-medium/hard-r2.py) |
| sol61-medium | hard | 3 | pass |  | 25 | 31 | 10 | 0 | 0.50 vs 0.77 | 0.30 | [hard-r3.py](sol61-medium/hard-r3.py) |
| sol61-medium | hard | 4 | pass |  | 25 | 31 | 9 | 0 | 0.13 vs 0.77 | 0.30 | [hard-r4.py](sol61-medium/hard-r4.py) |
| sol61-medium | hard | 5 | pass |  | 16 | 21 | 7 | 0 | 0.38 vs 0.77 | 0.27 | [hard-r5.py](sol61-medium/hard-r5.py) |
| sonnet-medium | hard | 1 | pass |  | 15 | 15 | 4 | 0 | 0.29 vs 0.77 | 0.26 | [hard-r1.py](sonnet-medium/hard-r1.py) |
| sonnet-medium | hard | 2 | pass |  | 33 | 38 | 7 | 0 | 0.67 vs 0.77 | 0.31 | [hard-r2.py](sonnet-medium/hard-r2.py) |
| sonnet-medium | hard | 3 | pass |  | 18 | 18 | 5 | 0 | 0.31 vs 0.77 | 0.26 | [hard-r3.py](sonnet-medium/hard-r3.py) |
| sonnet-medium | hard | 4 | pass |  | 25 | 30 | 9 | 0 | 1.27 vs 0.77 | 1.01 | [hard-r4.py](sonnet-medium/hard-r4.py) |
| sonnet-medium | hard | 5 | pass |  | 24 | 29 | 9 | 0 | 1.30 vs 0.77 | 1.01 | [hard-r5.py](sonnet-medium/hard-r5.py) |
