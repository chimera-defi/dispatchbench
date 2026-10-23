# p11_best_average (main L1-L6)

**Problem:** Largest average over contiguous subarrays of length >= k, as an exact reduced fraction.
**Signature:** `def best_average(a: list[int], k: int) -> list[int]:`

**Expected approach and traps:**
- Dinkelbach iteration (or a binary search in exact integer or rational arithmetic, never floats) on the ratio, using prefix sums and a running minimum prefix at distance >= k; the search itself must be exact, not just the final fraction. O(n) per iteration.
- Traps: float comparison fails when two averages differ by < 1e-9; the fraction must be in lowest terms; the best subarray can be longer than k.

**Results:** 74 pass, 9 fail of 83 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p11_best_average "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
