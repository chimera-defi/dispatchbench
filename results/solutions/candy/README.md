# candy (pilot)

**Problem:** Candy: minimum candies so each child gets at least one and a higher rating than a neighbour gets more.
**Signature:** `def candy(ratings: list[int]) -> int:`

**Expected approach and traps:**
- Two passes: left to right (rating up gives prev + 1), right to left (rating up gives next + 1), take the per-child max and sum. O(n).
- Traps: equal ratings impose no constraint; a single pass is not enough; the answer is the sum of maxima, not of either pass.

**Results:** 21 pass, 0 fail of 21 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the pilot's hidden checker: `python3 -I bench/pilot/checker.py candy <file.py>` (prints JSON with `pass`), or paste it into the original LeetCode problem.
