# p01_overlap_minutes (main L1-L6)

**Problem:** Total minutes (half-open intervals) covered by at least k meetings at once.
**Signature:** `def overlap_minutes(meetings: list[list[int]], k: int) -> int:`

**Expected approach and traps:**
- Sweep line: +1 at each start, -1 at each end, sort events, add the gap length whenever the running count is >= k. O(n log n).
- Traps: a meeting ending at t and one starting at t do not overlap; start == end covers nothing; times reach 10**9, so no per-minute loop.

**Results:** 43 pass, 0 fail of 43 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p01_overlap_minutes "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
