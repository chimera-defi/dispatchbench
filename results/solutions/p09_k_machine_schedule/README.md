# p09_k_machine_schedule (main L1-L6)

**Problem:** Max total pay of jobs that fit on k identical machines (half-open intervals).
**Signature:** `def k_machine_schedule(jobs: list[list[int]], k: int) -> int:`

**Expected approach and traps:**
- Min-cost flow: compress times into a line, k units of flow along time edges (cost 0), each job is a start->end edge of capacity 1 and cost -pay.
- Traps: greedy by end time or pay is wrong for weighted jobs; a job ending at t and one starting at t may share a machine; times up to 10**9 need compression.

**Results:** 77 pass, 7 fail of 84 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p09_k_machine_schedule "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
