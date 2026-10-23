# p11_best_average (main L1-L6)

**Problem:** Largest average over contiguous subarrays of length >= k, as an exact reduced fraction.
**Signature:** `def best_average(a: list[int], k: int) -> list[int]:`

**Expected approach and traps:**
- Binary search or Dinkelbach iteration on the ratio, using prefix sums and a running minimum prefix at distance >= k; finish with exact integer or `Fraction` arithmetic. O(n log) or fewer iterations.
- Traps: float comparison fails when two averages differ by < 1e-9; the fraction must be in lowest terms; the best subarray can be longer than k.

**Results:** 54 pass, 9 fail of 63 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p11_best_average "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
