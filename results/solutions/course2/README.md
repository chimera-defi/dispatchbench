# course2 (pilot)

**Problem:** Course Schedule II: return a valid order of courses given prerequisites, or [] if there is a cycle.
**Signature:** `def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:`

**Expected approach and traps:**
- Topological sort (Kahn's algorithm, or DFS with three colours). O(V + E).
- Traps: `[a, b]` means b before a; a cycle must give []; up to ~4M edges and recursion depth 2000 for DFS.

**Results:** 21 pass, 0 fail of 21 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the pilot's hidden checker: `python3 -I bench/pilot/checker.py course2 <file.py>` (prints JSON with `pass`), or paste it into the original LeetCode problem.
