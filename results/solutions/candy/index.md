# candy

Pilot problem (graded by `bench/pilot/checker.py`, not by `bench.grade`). Signature: `def candy(ratings: list[int]) -> int:`

Recoverable code: 21 trim-probe completions (`cache/trim/` keeps their text). The problem has 54 rows in `results/2026-10-22-pilot.jsonl` (54 passed); those rows store no code and the pilot's `runs/*.py` were not kept, so they cannot be shown. Outcome below is the row's own `passed` from the pilot checker.

| config | phase | rep | outcome | grade detail | LOC | lines | cc_max | lint | time exp (model vs ref) | mem ratio | file |
|---|---|---|---|---|---|---|---|---|---|---|---|
| haiku | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](haiku/trim-pair-r1.py) |
| haiku | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](haiku/trim-pair-r2.py) |
| haiku | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](haiku/trim-pair-r3.py) |
| luna-base | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](luna-base/trim-pair-r1.py) |
| luna-base | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](luna-base/trim-pair-r2.py) |
| luna-base | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](luna-base/trim-pair-r3.py) |
| luna-nofeat | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](luna-nofeat/trim-pair-r1.py) |
| luna-nofeat | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](luna-nofeat/trim-pair-r2.py) |
| luna-nofeat | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](luna-nofeat/trim-pair-r3.py) |
| luna-noshell | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](luna-noshell/trim-pair-r1.py) |
| luna-noshell | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](luna-noshell/trim-pair-r2.py) |
| luna-noshell | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](luna-noshell/trim-pair-r3.py) |
| terra-base | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](terra-base/trim-pair-r1.py) |
| terra-base | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](terra-base/trim-pair-r2.py) |
| terra-base | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](terra-base/trim-pair-r3.py) |
| terra-nofeat | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](terra-nofeat/trim-pair-r1.py) |
| terra-nofeat | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](terra-nofeat/trim-pair-r2.py) |
| terra-nofeat | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](terra-nofeat/trim-pair-r3.py) |
| terra-noshell | trim-pair | 1 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r1.py](terra-noshell/trim-pair-r1.py) |
| terra-noshell | trim-pair | 2 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r2.py](terra-noshell/trim-pair-r2.py) |
| terra-noshell | trim-pair | 3 | pass | pilot checker (row passed) | 10 | 13 | - | - | - vs - | - | [trim-pair-r3.py](terra-noshell/trim-pair-r3.py) |
