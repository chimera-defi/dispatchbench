# p15_paint_erase (hard L7)

**Problem:** Apply paint-if-not-darker and erase operations to a strip of up to 10**9 cells; report cell counts per colour.
**Signature:** `def paint(n: int, ops: list[list[int]]) -> list[list[int]]:`

**Expected approach and traps:**
- Compress coordinates from all l and r+1, then a segment tree with lazy `chmax(c)` for paint and `assign blank` for erase; read the leaves at the end, weighting by segment length.
- Traps: a plain interval map degrades to O(n^2) because higher colours are never removed; blank counts as lower than every colour; erase wins over earlier paint; n is too large for an array.

**Results:** 33 pass, 7 fail of 40 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p15_paint_erase "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
