# p06_calc (main L1-L6)

**Problem:** Evaluate an integer expression with + - * / % ^, unary minus and parentheses; return the int or "error".
**Signature:** `def calc(expr: str) -> int | str:`

**Expected approach and traps:**
- Recursive-descent or precedence-climbing parser on Python big ints, with the stated precedence: `^` right-assoc, then unary minus, then `* / %`, then `+ -`.
- Traps: `-2^2` is -4 but `2^-1` is an error; `/` truncates toward zero and `%` takes the dividend's sign (not Python `//` and `%`); `0^0` is 1; zero divisor or negative power anywhere is "error"; long `--` chains and depth-50 parentheses.

**Results:** 58 pass, 5 fail of 63 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the hidden tests: `python3 -m bench.grade p06_calc "$PWD/<file.py>"` (absolute path needed; prints JSON with `outcome`).
