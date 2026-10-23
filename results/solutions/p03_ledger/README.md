# p03_ledger (main L1-L6)

**Problem:** Simulate bank operations with freeze rules and undo; return final balances and the indices of failed ops.
**Signature:** `def ledger(ops: list[str]) -> tuple[dict[str, int], list[int]]:`

**Expected approach and traps:**
- Dict of balances plus a stack of inverse actions for each successful non-undo op; `undo` pops the stack. O(n).
- Traps: amount must be all digits (no sign, `007` ok); open allows 0, other amounts need > 0; deposit and transfer-target may be frozen; failed ops change nothing and are not undoable; failed undo is rejected.

**Results:** 79 pass, 4 fail of 83 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p03_ledger "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
