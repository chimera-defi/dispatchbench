# p13_xor_ring (hard L7)

**Problem:** Apply a XOR-of-offsets update to a ring of lamps t times (t up to 10**18).
**Signature:** `def evolve(state: str, offsets: list[int], t: int) -> str:`

**Expected approach and traps:**
- The step is multiplication by a polynomial in GF(2)[x]/(x^n - 1); square-and-multiply the polynomial (carry-less multiply on Python ints) and apply it once. About 60 squarings.
- Traps: reduce negative or huge offsets mod n; duplicate offsets cancel; direction is `(i + d) mod n`; t = 0 returns the input; simulating t steps is impossible.

**Results:** 37 pass, 3 fail of 40 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p13_xor_ring "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
