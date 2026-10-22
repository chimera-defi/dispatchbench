# p12_sheet

Rung L6. Signature: `def sheet(cells: dict[str, str]) -> dict[str, int | str]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku-low | main | 1 | crash | large case 0: RecursionError: maximum recursion depth exceeded | 239 | 268 | 30 | 0 | - vs - | - | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 190 | 215 | 28 | 0 | 1.13 vs 1.13 | 0.25 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 198 | 222 | 29 | 2 | 1.18 vs 1.13 | 0.22 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 169 | 187 | 27 | 0 | 1.14 vs 1.13 | 0.21 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 211 | 231 | 18 | 0 | 1.05 vs 1.13 | 1.05 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-medium | main | 1 | pass |  | 214 | 239 | 26 | 0 | 0.94 vs 1.13 | 0.22 | [main-r1.py](haiku-medium/main-r1.py) |
| haiku-medium | main | 2 | pass |  | 182 | 207 | 27 | 0 | 1.07 vs 1.13 | 1.10 | [main-r2.py](haiku-medium/main-r2.py) |
| haiku-medium | main | 3 | pass |  | 181 | 207 | 25 | 0 | 1.04 vs 1.13 | 0.13 | [main-r3.py](haiku-medium/main-r3.py) |
| haiku-medium | main | 4 | pass |  | 203 | 225 | 32 | 1 | 1.08 vs 1.13 | 0.25 | [main-r4.py](haiku-medium/main-r4.py) |
| haiku-medium | main | 5 | pass |  | 208 | 231 | 26 | 0 | 0.92 vs 1.13 | 0.23 | [main-r5.py](haiku-medium/main-r5.py) |
| luna-high | escalation | 1 | crash | small case 1: ValueError: Invalid formula | 183 | 204 | 27 | 0 | - vs - | - | [escalation-r1.py](luna-high/escalation-r1.py) |
| luna-high | escalation | 2 | pass |  | 188 | 207 | 27 | 0 | 1.07 vs 1.13 | 1.09 | [escalation-r2.py](luna-high/escalation-r2.py) |
| luna-high | escalation | 3 | pass |  | 176 | 207 | 28 | 0 | 1.00 vs 1.13 | 0.13 | [escalation-r3.py](luna-high/escalation-r3.py) |
| luna-high | escalation | 4 | pass |  | 207 | 225 | 28 | 0 | 1.11 vs 1.13 | 0.99 | [escalation-r4.py](luna-high/escalation-r4.py) |
| luna-high | escalation | 5 | crash | small case 0: error: bad character range =-< at position 34 | 185 | 205 | 27 | 0 | - vs - | - | [escalation-r5.py](luna-high/escalation-r5.py) |
| luna-low | main | 1 | crash | small case 0: ValueError: Invalid formula | 196 | 226 | 27 | 0 | - vs - | - | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | crash | small case 1: ValueError: Invalid formula | 177 | 198 | 5 | 0 | - vs - | - | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | crash | small case 0: ValueError: Invalid formula | 190 | 215 | 29 | 0 | - vs - | - | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | wrong | small case 0 | 191 | 216 | 5 | 2 | - vs - | - | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | crash | large case 0: RecursionError: maximum recursion depth exceeded | 177 | 192 | 28 | 0 | - vs - | - | [main-r5.py](luna-low/main-r5.py) |
| luna-low-bare | exploratory | 1 | crash | large case 0: RecursionError: maximum recursion depth exceeded | 202 | 224 | 27 | 0 | - vs - | - | [exploratory-r1.py](luna-low-bare/exploratory-r1.py) |
| luna-low-bare | exploratory | 2 | crash | small case 1: ValueError: Invalid formula | 182 | 197 | 27 | 0 | - vs - | - | [exploratory-r2.py](luna-low-bare/exploratory-r2.py) |
| luna-low-bare | exploratory | 3 | crash | small case 1: ValueError: invalid literal for int() with base 10: '' | 227 | 264 | 6 | 2 | - vs - | - | [exploratory-r3.py](luna-low-bare/exploratory-r3.py) |
| luna-low-bare | exploratory | 4 | crash | small case 1: ValueError: invalid identifier | 180 | 210 | 19 | 1 | - vs - | - | [exploratory-r4.py](luna-low-bare/exploratory-r4.py) |
| luna-low-bare | exploratory | 5 | wrong | small case 2 | 197 | 219 | 5 | 0 | - vs - | - | [exploratory-r5.py](luna-low-bare/exploratory-r5.py) |
| luna-medium | main | 1 | crash | small case 0: ValueError: Invalid cell | 208 | 228 | 31 | 2 | - vs - | - | [main-r1.py](luna-medium/main-r1.py) |
| luna-medium | main | 2 | wrong | small case 1 | 200 | 214 | 30 | 0 | - vs - | - | [main-r2.py](luna-medium/main-r2.py) |
| luna-medium | main | 3 | crash | large case 0: RecursionError: maximum recursion depth exceeded | 184 | 207 | 29 | 0 | - vs - | - | [main-r3.py](luna-medium/main-r3.py) |
| luna-medium | main | 4 | crash | small case 0: ValueError: Invalid formula | 183 | 202 | 19 | 0 | - vs - | - | [main-r4.py](luna-medium/main-r4.py) |
| luna-medium | main | 5 | crash | small case 0: ValueError: Invalid atom | 200 | 230 | 28 | 0 | - vs - | - | [main-r5.py](luna-medium/main-r5.py) |
| sol61-medium | main | 1 | pass |  | 215 | 244 | 42 | 0 | 0.87 vs 1.13 | 0.13 | [main-r1.py](sol61-medium/main-r1.py) |
| sol61-medium | main | 2 | crash | small case 18: TypeError: unhashable type: 'list' | 220 | 246 | 46 | 0 | - vs - | - | [main-r2.py](sol61-medium/main-r2.py) |
| sol61-medium | main | 3 | pass |  | 218 | 253 | 47 | 0 | 0.99 vs 1.13 | 0.13 | [main-r3.py](sol61-medium/main-r3.py) |
| sol61-medium | main | 4 | pass |  | 205 | 235 | 44 | 0 | 1.10 vs 1.13 | 0.13 | [main-r4.py](sol61-medium/main-r4.py) |
| sol61-medium | main | 5 | crash | small case 18: TypeError: unhashable type: 'list' | 179 | 207 | 34 | 0 | - vs - | - | [main-r5.py](sol61-medium/main-r5.py) |
| sonnet-medium | main | 1 | pass |  | 187 | 209 | 34 | 1 | 1.08 vs 1.13 | 1.00 | [main-r1.py](sonnet-medium/main-r1.py) |
| sonnet-medium | main | 2 | pass |  | 192 | 214 | 32 | 3 | 0.99 vs 1.13 | 0.13 | [main-r2.py](sonnet-medium/main-r2.py) |
| sonnet-medium | main | 3 | pass |  | 205 | 227 | 32 | 2 | 1.01 vs 1.13 | 0.14 | [main-r3.py](sonnet-medium/main-r3.py) |
| sonnet-medium | main | 4 | pass |  | 187 | 209 | 32 | 1 | 1.14 vs 1.13 | 0.14 | [main-r4.py](sonnet-medium/main-r4.py) |
| sonnet-medium | main | 5 | pass |  | 199 | 223 | 31 | 2 | 0.97 vs 1.13 | 0.14 | [main-r5.py](sonnet-medium/main-r5.py) |
