# p10_avoid_count (main L1-L6)

**Problem:** Count length-n strings over a small alphabet that contain no banned substring, mod 1e9+7, with n up to 10**18.
**Signature:** `def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:`

**Expected approach and traps:**
- Build an Aho-Corasick automaton (at most 21 states), mark a state bad if it or any suffix-link ancestor ends a banned word, then raise the transition matrix to the n-th power. O(S^3 log n).
- Traps: banned words that contain others or repeat; the bad flag must propagate through failure links; n = 0 gives 1; linear DP over n cannot reach 10**18.

**Results:** 79 pass, 5 fail of 84 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p10_avoid_count "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
