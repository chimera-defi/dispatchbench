# p12_sheet (main L1-L6)

**Problem:** Evaluate a spreadsheet of integers and formulas (SUM/MIN/MAX/IF, ranges) with #DIV/0! and #CYCLE! errors.
**Signature:** `def sheet(cells: dict[str, str]) -> dict[str, int | str]:`

**Expected approach and traps:**
- Recursive-descent formula parser plus memoised evaluation of cells with an in-progress marker; a reference to an in-progress cell yields #CYCLE!.
- Traps: strict left-to-right error order; IF evaluates only the chosen branch; ranges skip missing cells but a missing-cell formula argument counts as 0; truncating division; reference chains up to 2574 deep exceed Python's default recursion limit.

**Results:** 44 pass, 24 fail of 68 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p12_sheet "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
