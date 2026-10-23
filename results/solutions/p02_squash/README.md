# p02_squash (main L1-L6)

**Problem:** Run-length encode a string; runs of 1-2 are written out, runs of 3+ become count + char; digits and backslash are escaped.
**Signature:** `def squash(s: str) -> str:`

**Expected approach and traps:**
- One pass over maximal runs; run >= 3 gives str(len) + esc(c), shorter runs give esc(c) repeated. O(n) with a list join.
- Traps: the escape applies to every written char (also inside short runs); the count itself is never escaped; empty string; `+=` on 200k chars.

**Results:** 63 pass, 0 fail of 63 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p02_squash "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
