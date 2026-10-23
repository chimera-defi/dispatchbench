# p12_sheet

Rung L6. Signature: `def sheet(cells: dict[str, str]) -> dict[str, int | str]:`

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| astra-medium | exploratory | 1 | pass |  | 229 | 259 | - | - | - vs - | - | [exploratory-r1.py](astra-medium/exploratory-r1.py) |
| astra-medium | exploratory | 2 | pass |  | 205 | 232 | - | - | - vs - | - | [exploratory-r2.py](astra-medium/exploratory-r2.py) |
| astra-medium | exploratory | 3 | pass |  | 203 | 227 | - | - | - vs - | - | [exploratory-r3.py](astra-medium/exploratory-r3.py) |
| astra-medium | exploratory | 4 | pass |  | 214 | 241 | - | - | - vs - | - | [exploratory-r4.py](astra-medium/exploratory-r4.py) |
| astra-medium | exploratory | 5 | pass |  | 206 | 230 | - | - | - vs - | - | [exploratory-r5.py](astra-medium/exploratory-r5.py) |
| haiku-low | main | 1 | crash | large case 0: RecursionError: maximum recursion depth exceeded | 239 | 268 | 30 | 0 | - vs - | - | [main-r1.py](haiku-low/main-r1.py) |
| haiku-low | main | 2 | pass |  | 190 | 215 | 28 | 0 | 1.13 vs 1.13 | 0.25 | [main-r2.py](haiku-low/main-r2.py) |
| haiku-low | main | 3 | pass |  | 198 | 222 | 29 | 2 | 1.18 vs 1.13 | 0.22 | [main-r3.py](haiku-low/main-r3.py) |
| haiku-low | main | 4 | pass |  | 169 | 187 | 27 | 0 | 1.14 vs 1.13 | 0.21 | [main-r4.py](haiku-low/main-r4.py) |
| haiku-low | main | 5 | pass |  | 211 | 231 | 18 | 0 | 1.05 vs 1.13 | 1.05 | [main-r5.py](haiku-low/main-r5.py) |
| haiku-low-plan+luna-high-bare | f-build | 1 | pass |  | 199 | 220 | - | - | - vs - | - | [f-build-r1.py](haiku-low-plan+luna-high-bare/f-build-r1.py) |
| haiku-low-plan+luna-high-bare | f-build | 2 | crash |  | 212 | 233 | - | - | - vs - | - | [f-build-r2.py](haiku-low-plan+luna-high-bare/f-build-r2.py) |
| haiku-low-plan+luna-high-bare | f-build | 3 | crash |  | 206 | 226 | - | - | - vs - | - | [f-build-r3.py](haiku-low-plan+luna-high-bare/f-build-r3.py) |
| haiku-low-plan+luna-high-bare | f-build | 4 | pass |  | 228 | 266 | - | - | - vs - | - | [f-build-r4.py](haiku-low-plan+luna-high-bare/f-build-r4.py) |
| haiku-low-plan+luna-high-bare | f-build | 5 | pass |  | 207 | 230 | - | - | - vs - | - | [f-build-r5.py](haiku-low-plan+luna-high-bare/f-build-r5.py) |
| haiku-low-plan+luna-low | f-build | 1 | pass |  | 223 | 244 | - | - | - vs - | - | [f-build-r1.py](haiku-low-plan+luna-low/f-build-r1.py) |
| haiku-low-plan+luna-low | f-build | 2 | pass |  | 198 | 227 | - | - | - vs - | - | [f-build-r2.py](haiku-low-plan+luna-low/f-build-r2.py) |
| haiku-low-plan+luna-low | f-build | 3 | crash |  | 193 | 211 | - | - | - vs - | - | [f-build-r3.py](haiku-low-plan+luna-low/f-build-r3.py) |
| haiku-low-plan+luna-low | f-build | 4 | pass |  | 222 | 239 | - | - | - vs - | - | [f-build-r4.py](haiku-low-plan+luna-low/f-build-r4.py) |
| haiku-low-plan+luna-low | f-build | 5 | pass |  | 182 | 201 | - | - | - vs - | - | [f-build-r5.py](haiku-low-plan+luna-low/f-build-r5.py) |
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
| luna-high-bare+haiku-on-fail | g-build | 1 | cached |  | 193 | 212 | - | - | - vs - | - | [g-build-r1.py](luna-high-bare+haiku-on-fail/g-build-r1.py) |
| luna-high-bare+haiku-on-fail | g-build | 2 | cached |  | 188 | 208 | - | - | - vs - | - | [g-build-r2.py](luna-high-bare+haiku-on-fail/g-build-r2.py) |
| luna-high-bare+haiku-on-fail | g-build | 3 | cached |  | 165 | 185 | - | - | - vs - | - | [g-build-r3.py](luna-high-bare+haiku-on-fail/g-build-r3.py) |
| luna-high-bare+haiku-on-fail | g-build | 4 | cached |  | 181 | 199 | - | - | - vs - | - | [g-build-r4.py](luna-high-bare+haiku-on-fail/g-build-r4.py) |
| luna-high-bare+haiku-on-fail | g-build | 5 | cached |  | 183 | 204 | - | - | - vs - | - | [g-build-r5.py](luna-high-bare+haiku-on-fail/g-build-r5.py) |
| luna-high-bare+haiku-on-fail | g-repair | 2 | pass |  | 190 | 210 | - | - | - vs - | - | [g-repair-r2.py](luna-high-bare+haiku-on-fail/g-repair-r2.py) |
| luna-high-bare+haiku-on-fail | g-repair | 5 | pass |  | 184 | 205 | - | - | - vs - | - | [g-repair-r5.py](luna-high-bare+haiku-on-fail/g-repair-r5.py) |
| luna-high-bare+haiku-review-all | g-repair | 1 | pass |  | 193 | 212 | - | - | - vs - | - | [g-repair-r1.py](luna-high-bare+haiku-review-all/g-repair-r1.py) |
| luna-high-bare+haiku-review-all | g-repair | 2 | pass |  | 188 | 208 | - | - | - vs - | - | [g-repair-r2.py](luna-high-bare+haiku-review-all/g-repair-r2.py) |
| luna-high-bare+haiku-review-all | g-repair | 3 | pass |  | 165 | 185 | - | - | - vs - | - | [g-repair-r3.py](luna-high-bare+haiku-review-all/g-repair-r3.py) |
| luna-high-bare+haiku-review-all | g-repair | 4 | pass |  | 200 | 221 | - | - | - vs - | - | [g-repair-r4.py](luna-high-bare+haiku-review-all/g-repair-r4.py) |
| luna-high-bare+haiku-review-all | g-repair | 5 | pass |  | 183 | 204 | - | - | - vs - | - | [g-repair-r5.py](luna-high-bare+haiku-review-all/g-repair-r5.py) |
| luna-high-bare+retry-on-fail | g-repair | 2 | pass |  | 189 | 222 | - | - | - vs - | - | [g-repair-r2.py](luna-high-bare+retry-on-fail/g-repair-r2.py) |
| luna-high-bare+retry-on-fail | g-repair | 5 | pass |  | 193 | 225 | - | - | - vs - | - | [g-repair-r5.py](luna-high-bare+retry-on-fail/g-repair-r5.py) |
| luna-low | main | 1 | crash | small case 0: ValueError: Invalid formula | 196 | 226 | 27 | 0 | - vs - | - | [main-r1.py](luna-low/main-r1.py) |
| luna-low | main | 2 | crash | small case 1: ValueError: Invalid formula | 177 | 198 | 5 | 0 | - vs - | - | [main-r2.py](luna-low/main-r2.py) |
| luna-low | main | 3 | crash | small case 0: ValueError: Invalid formula | 190 | 215 | 29 | 0 | - vs - | - | [main-r3.py](luna-low/main-r3.py) |
| luna-low | main | 4 | wrong | small case 0 | 191 | 216 | 5 | 2 | - vs - | - | [main-r4.py](luna-low/main-r4.py) |
| luna-low | main | 5 | crash | large case 0: RecursionError: maximum recursion depth exceeded | 177 | 192 | 28 | 0 | - vs - | - | [main-r5.py](luna-low/main-r5.py) |
| luna-low+haiku-on-fail | g-build | 1 | cached |  | 185 | 210 | - | - | - vs - | - | [g-build-r1.py](luna-low+haiku-on-fail/g-build-r1.py) |
| luna-low+haiku-on-fail | g-build | 2 | cached |  | 189 | 210 | - | - | - vs - | - | [g-build-r2.py](luna-low+haiku-on-fail/g-build-r2.py) |
| luna-low+haiku-on-fail | g-build | 3 | cached |  | 199 | 216 | - | - | - vs - | - | [g-build-r3.py](luna-low+haiku-on-fail/g-build-r3.py) |
| luna-low+haiku-on-fail | g-build | 4 | cached |  | 197 | 229 | - | - | - vs - | - | [g-build-r4.py](luna-low+haiku-on-fail/g-build-r4.py) |
| luna-low+haiku-on-fail | g-build | 5 | cached |  | 314 | 344 | - | - | - vs - | - | [g-build-r5.py](luna-low+haiku-on-fail/g-build-r5.py) |
| luna-low+haiku-on-fail | g-repair | 1 | pass |  | 219 | 245 | - | - | - vs - | - | [g-repair-r1.py](luna-low+haiku-on-fail/g-repair-r1.py) |
| luna-low+haiku-on-fail | g-repair | 2 | pass |  | 178 | 205 | - | - | - vs - | - | [g-repair-r2.py](luna-low+haiku-on-fail/g-repair-r2.py) |
| luna-low+haiku-on-fail | g-repair | 3 | pass |  | 207 | 224 | - | - | - vs - | - | [g-repair-r3.py](luna-low+haiku-on-fail/g-repair-r3.py) |
| luna-low+haiku-on-fail | g-repair | 5 | pass |  | 213 | 237 | - | - | - vs - | - | [g-repair-r5.py](luna-low+haiku-on-fail/g-repair-r5.py) |
| luna-low+haiku-review-all | g-repair | 1 | pass |  | 207 | 233 | - | - | - vs - | - | [g-repair-r1.py](luna-low+haiku-review-all/g-repair-r1.py) |
| luna-low+haiku-review-all | g-repair | 2 | wrong |  | 178 | 207 | - | - | - vs - | - | [g-repair-r2.py](luna-low+haiku-review-all/g-repair-r2.py) |
| luna-low+haiku-review-all | g-repair | 3 | pass |  | 202 | 220 | - | - | - vs - | - | [g-repair-r3.py](luna-low+haiku-review-all/g-repair-r3.py) |
| luna-low+haiku-review-all | g-repair | 4 | pass |  | 201 | 234 | - | - | - vs - | - | [g-repair-r4.py](luna-low+haiku-review-all/g-repair-r4.py) |
| luna-low+haiku-review-all | g-repair | 5 | pass |  | 217 | 237 | - | - | - vs - | - | [g-repair-r5.py](luna-low+haiku-review-all/g-repair-r5.py) |
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
| luna56-high | exploratory | 1 | pass |  | 193 | 238 | - | - | - vs - | - | [exploratory-r1.py](luna56-high/exploratory-r1.py) |
| luna56-high | exploratory | 2 | pass |  | 222 | 269 | - | - | - vs - | - | [exploratory-r2.py](luna56-high/exploratory-r2.py) |
| luna56-high | exploratory | 3 | pass |  | 236 | 288 | - | - | - vs - | - | [exploratory-r3.py](luna56-high/exploratory-r3.py) |
| luna56-high | exploratory | 4 | crash | small case 18: TypeError: unsupported operand type(s) for +: 'int' ... | 225 | 278 | - | - | - vs - | - | [exploratory-r4.py](luna56-high/exploratory-r4.py) |
| luna56-high | exploratory | 5 | crash | small case 25: TypeError: 'int' object is not subscriptable | 192 | 232 | - | - | - vs - | - | [exploratory-r5.py](luna56-high/exploratory-r5.py) |
| luna56-low | exploratory | 1 | pass |  | 204 | 241 | - | - | - vs - | - | [exploratory-r1.py](luna56-low/exploratory-r1.py) |
| luna56-low | exploratory | 2 | crash | small case 4: IndexError: list index out of range | 192 | 229 | - | - | - vs - | - | [exploratory-r2.py](luna56-low/exploratory-r2.py) |
| luna56-low | exploratory | 3 | crash | small case 1: ValueError: | 202 | 245 | - | - | - vs - | - | [exploratory-r3.py](luna56-low/exploratory-r3.py) |
| luna56-low | exploratory | 4 | wrong | small case 18 | 203 | 232 | - | - | - vs - | - | [exploratory-r4.py](luna56-low/exploratory-r4.py) |
| luna56-low | exploratory | 5 | crash | small case 3: ValueError: | 201 | 224 | - | - | - vs - | - | [exploratory-r5.py](luna56-low/exploratory-r5.py) |
| sol56-high | exploratory | 1 | pass |  | 211 | 258 | - | - | - vs - | - | [exploratory-r1.py](sol56-high/exploratory-r1.py) |
| sol56-high | exploratory | 2 | pass |  | 217 | 260 | - | - | - vs - | - | [exploratory-r2.py](sol56-high/exploratory-r2.py) |
| sol56-high | exploratory | 3 | pass |  | 212 | 255 | - | - | - vs - | - | [exploratory-r3.py](sol56-high/exploratory-r3.py) |
| sol56-high | exploratory | 4 | pass |  | 222 | 267 | - | - | - vs - | - | [exploratory-r4.py](sol56-high/exploratory-r4.py) |
| sol56-high | exploratory | 5 | pass |  | 299 | 369 | - | - | - vs - | - | [exploratory-r5.py](sol56-high/exploratory-r5.py) |
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
