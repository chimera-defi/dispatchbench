# p08_recur (main L1-L6)

**Problem:** Expand a calendar recurrence rule (daily, weekly, monthly by day or by nth weekday, yearly) into the first count dates.
**Signature:** `def recur(start: str, rule: str, count: int) -> list[str]:`

**Expected approach and traps:**
- Generate candidates per rule with `datetime`/`calendar` and keep those >= start: step K days; active weeks counted from the Monday of start's week; active months counted from start's month.
- Traps: a month without day D is skipped, never clamped; -1 means last day or last such weekday; a missing 5th weekday contributes nothing; `02-29` only in leap years (1900, 2100, 2200, 2300 are not leap); start itself is included if it matches.

**Results:** 61 pass, 2 fail of 63 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p08_recur "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
