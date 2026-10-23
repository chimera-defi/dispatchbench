# p14_bounce_board (hard L7)

**Problem:** Expected number of turns to finish a dice board with bounce-back and jumps, as an exact fraction, or None if the game may never end.
**Signature:** `def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:`

**Expected approach and traps:**
- Resolve jump chains into a transition table, find states reachable from 0 that cannot reach cell n (then answer None), and solve E = 1 + P*E by Gaussian elimination with `Fraction`s.
- Traps: bounce formula `2n - p - r`; jumps within the same turn; non-termination must be decided by graph reachability, not by a float result; reduce the fraction.

**Results:** 20 pass, 0 fail of 20 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p14_bounce_board "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
