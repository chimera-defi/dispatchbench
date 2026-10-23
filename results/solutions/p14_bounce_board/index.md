# p14_bounce_board

Rung L7. Signature: `def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| astra-medium | hard | 1 | pass |  | 80 | 100 | - | - | - vs - | - | [hard-r1.py](astra-medium/hard-r1.py) |
| astra-medium | hard | 2 | pass |  | 76 | 96 | - | - | - vs - | - | [hard-r2.py](astra-medium/hard-r2.py) |
| astra-medium | hard | 3 | pass |  | 81 | 101 | - | - | - vs - | - | [hard-r3.py](astra-medium/hard-r3.py) |
| astra-medium | hard | 4 | pass |  | 85 | 101 | - | - | - vs - | - | [hard-r4.py](astra-medium/hard-r4.py) |
| astra-medium | hard | 5 | pass |  | 81 | 100 | - | - | - vs - | - | [hard-r5.py](astra-medium/hard-r5.py) |
| haiku-low | hard | 1 | pass |  | 68 | 84 | 33 | 1 | 2.64 vs 2.22 | 0.27 | [hard-r1.py](haiku-low/hard-r1.py) |
| haiku-low | hard | 2 | pass |  | 62 | 81 | 30 | 1 | 2.80 vs 2.22 | 0.25 | [hard-r2.py](haiku-low/hard-r2.py) |
| haiku-low | hard | 3 | pass |  | 65 | 83 | 33 | 1 | 2.82 vs 2.22 | 0.27 | [hard-r3.py](haiku-low/hard-r3.py) |
| haiku-low | hard | 4 | pass |  | 56 | 73 | 31 | 1 | 2.88 vs 2.22 | 0.26 | [hard-r4.py](haiku-low/hard-r4.py) |
| haiku-low | hard | 5 | pass |  | 63 | 82 | 31 | 1 | 2.72 vs 2.22 | 0.26 | [hard-r5.py](haiku-low/hard-r5.py) |
| luna-high | hard | 1 | pass |  | 68 | 81 | 33 | 0 | 2.53 vs 2.22 | 0.29 | [hard-r1.py](luna-high/hard-r1.py) |
| luna-high | hard | 2 | pass |  | 75 | 92 | 29 | 0 | 2.13 vs 2.22 | 0.13 | [hard-r2.py](luna-high/hard-r2.py) |
| luna-high | hard | 3 | pass |  | 71 | 90 | 36 | 0 | 2.75 vs 2.22 | 0.29 | [hard-r3.py](luna-high/hard-r3.py) |
| luna-high | hard | 4 | pass |  | 64 | 78 | 30 | 0 | 2.21 vs 2.22 | 0.25 | [hard-r4.py](luna-high/hard-r4.py) |
| luna-high | hard | 5 | pass |  | 77 | 94 | 34 | 0 | 2.08 vs 2.22 | 0.29 | [hard-r5.py](luna-high/hard-r5.py) |
| luna56-high | hard | 1 | pass |  | 59 | 73 | - | - | - vs - | - | [hard-r1.py](luna56-high/hard-r1.py) |
| luna56-high | hard | 2 | pass |  | 71 | 89 | - | - | - vs - | - | [hard-r2.py](luna56-high/hard-r2.py) |
| luna56-high | hard | 3 | crash | small case 12: StopIteration: | 58 | 73 | - | - | - vs - | - | [hard-r3.py](luna56-high/hard-r3.py) |
| luna56-high | hard | 4 | crash | small case 0: AttributeError: 'float' object has no attribute 'nume... | 60 | 77 | - | - | - vs - | - | [hard-r4.py](luna56-high/hard-r4.py) |
| luna56-high | hard | 5 | crash | small case 0: AttributeError: 'float' object has no attribute 'nume... | 66 | 83 | - | - | - vs - | - | [hard-r5.py](luna56-high/hard-r5.py) |
| luna56-low | hard | 1 | crash | small case 11: StopIteration: | 74 | 91 | - | - | - vs - | - | [hard-r1.py](luna56-low/hard-r1.py) |
| luna56-low | hard | 2 | crash | small case 11: StopIteration: | 63 | 81 | - | - | - vs - | - | [hard-r2.py](luna56-low/hard-r2.py) |
| luna56-low | hard | 3 | pass |  | 68 | 84 | - | - | - vs - | - | [hard-r3.py](luna56-low/hard-r3.py) |
| luna56-low | hard | 4 | crash | small case 11: KeyError: 2 | 60 | 78 | - | - | - vs - | - | [hard-r4.py](luna56-low/hard-r4.py) |
| luna56-low | hard | 5 | pass |  | 73 | 89 | - | - | - vs - | - | [hard-r5.py](luna56-low/hard-r5.py) |
| sol56-high | hard | 1 | pass |  | 74 | 89 | - | - | - vs - | - | [hard-r1.py](sol56-high/hard-r1.py) |
| sol56-high | hard | 2 | pass |  | 74 | 91 | - | - | - vs - | - | [hard-r2.py](sol56-high/hard-r2.py) |
| sol56-high | hard | 3 | pass |  | 97 | 125 | - | - | - vs - | - | [hard-r3.py](sol56-high/hard-r3.py) |
| sol56-high | hard | 4 | crash | small case 0: AttributeError: 'float' object has no attribute 'nume... | 86 | 105 | - | - | - vs - | - | [hard-r4.py](sol56-high/hard-r4.py) |
| sol56-high | hard | 5 | crash | small case 0: AttributeError: 'float' object has no attribute 'nume... | 89 | 109 | - | - | - vs - | - | [hard-r5.py](sol56-high/hard-r5.py) |
| sol61-medium | hard | 1 | pass |  | 78 | 96 | 29 | 0 | 2.14 vs 2.22 | 0.13 | [hard-r1.py](sol61-medium/hard-r1.py) |
| sol61-medium | hard | 2 | pass |  | 80 | 96 | 35 | 0 | 2.12 vs 2.22 | 0.14 | [hard-r2.py](sol61-medium/hard-r2.py) |
| sol61-medium | hard | 3 | pass |  | 75 | 92 | 28 | 0 | 2.04 vs 2.22 | 0.14 | [hard-r3.py](sol61-medium/hard-r3.py) |
| sol61-medium | hard | 4 | pass |  | 77 | 94 | 29 | 0 | 2.07 vs 2.22 | 0.13 | [hard-r4.py](sol61-medium/hard-r4.py) |
| sol61-medium | hard | 5 | pass |  | 84 | 102 | 33 | 0 | 2.15 vs 2.22 | 0.13 | [hard-r5.py](sol61-medium/hard-r5.py) |
| sonnet-medium | hard | 1 | pass |  | 76 | 88 | 30 | 0 | 2.64 vs 2.22 | 0.26 | [hard-r1.py](sonnet-medium/hard-r1.py) |
| sonnet-medium | hard | 2 | pass |  | 70 | 80 | 34 | 1 | 2.75 vs 2.22 | 0.30 | [hard-r2.py](sonnet-medium/hard-r2.py) |
| sonnet-medium | hard | 3 | pass |  | 67 | 78 | 30 | 1 | 2.86 vs 2.22 | 0.24 | [hard-r3.py](sonnet-medium/hard-r3.py) |
| sonnet-medium | hard | 4 | pass |  | 67 | 78 | 31 | 1 | 2.71 vs 2.22 | 0.26 | [hard-r4.py](sonnet-medium/hard-r4.py) |
| sonnet-medium | hard | 5 | pass |  | 74 | 85 | 34 | 1 | 2.86 vs 2.22 | 0.28 | [hard-r5.py](sonnet-medium/hard-r5.py) |
