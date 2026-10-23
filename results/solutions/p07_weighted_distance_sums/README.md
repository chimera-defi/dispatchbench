# p07_weighted_distance_sums (main L1-L6)

**Problem:** For every tree node v, sum over nodes u of w[u] * dist(u, v).
**Signature:** `def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:`

**Expected approach and traps:**
- Rerooting: compute S(0) and subtree weights once, then S(child) = S(parent) + W_total - 2 * sub[child]. O(n).
- Traps: n = 200000 path breaks recursive DFS (use an iterative order); O(n^2) all-pairs is too slow.

**Results:** 61 pass, 2 fail of 63 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p07_weighted_distance_sums "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
