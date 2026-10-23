# minwindow (pilot)

**Problem:** Minimum Window Substring: shortest substring of s containing every character of t with multiplicity.
**Signature:** `def minWindow(s: str, t: str) -> str:`

**Expected approach and traps:**
- Sliding window with a need-count map and a formed counter; expand right, shrink left while valid. O(m + n).
- Traps: duplicates in t; case-sensitive; return "" when no window exists; 10**5 length rules out O(n^2).

**Results:** No answer code is recoverable for this problem. See [index.md](index.md).

**To verify for yourself:** run it against the pilot's hidden checker: `python3 -I bench/pilot/checker.py minwindow <file.py>` (prints JSON with `pass`), or paste it into the original LeetCode problem.
