# wildcard (pilot)

**Problem:** Wildcard Matching: does pattern p with ? and * match all of s?
**Signature:** `def isMatch(s: str, p: str) -> bool:`

**Expected approach and traps:**
- O(m*n) DP, or greedy two pointers that remember the last `*` and backtrack to it.
- Traps: `*` may match empty; consecutive and trailing stars; empty s or p; plain recursion is exponential.

**Results:** No answer code is recoverable for this problem. See [index.md](index.md).

**To verify for yourself:** run it against the pilot's hidden checker: `python3 -I bench/pilot/checker.py wildcard <file.py>` (prints JSON with `pass`), or paste it into the original LeetCode problem.
