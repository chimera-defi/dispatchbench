# p04_taller_within (main L1-L6)

**Problem:** For each position, count strictly taller people among the k directly in front.
**Signature:** `def taller_within(a: list[int], k: int) -> list[int]:`

**Expected approach and traps:**
- Sliding window over the last k values with a Fenwick tree over compressed heights (add a[i], remove a[i-k]); query count greater than a[i]. O(n log n).
- Traps: O(n*k) brute force times out at 200k; strict `>`; k = 0 gives all zeros; k larger than the prefix.

**Results:** 73 pass, 14 fail of 87 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p04_taller_within "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
