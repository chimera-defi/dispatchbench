# itinerary (pilot)

**Problem:** Reconstruct Itinerary: use every ticket once from JFK, lexically smallest itinerary.
**Signature:** `def findItinerary(tickets: list[list[str]]) -> list[str]:`

**Expected approach and traps:**
- Hierholzer's algorithm with neighbours kept in sorted order (heap): DFS, append airport after its edges are used, reverse. O(E log E).
- Traps: plain greedy DFS gets stuck in dead ends; duplicate tickets; must use all tickets.

**Results:** No answer code is recoverable for this problem. See [index.md](index.md).

**To verify for yourself:** run it against the pilot's hidden checker: `python3 -I bench/pilot/checker.py itinerary <file.py>` (prints JSON with `pass`), or paste it into the original LeetCode problem.
