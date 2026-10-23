# p05_pass_route (main L1-L6)

**Problem:** Cheapest trip from stop 0 to n-1 where zone passes can be bought at listed stations to make that zone's rides free.
**Signature:** `def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:`

**Expected approach and traps:**
- Dijkstra over states (stop, set of bought zones); at most 4 zones so 16 masks. Buying at a station is an edge to the same stop with a bigger mask. About 32k states.
- Traps: a pass can only be bought while standing at its station; zone -1 is never free; parallel rides; buying a pass twice; unreachable gives -1.

**Results:** 41 pass, 2 fail of 43 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p05_pass_route "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
