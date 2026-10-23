# fizzbuzz (pilot)

**Problem:** Return 1..n as strings, with Fizz, Buzz and FizzBuzz for multiples of 3, 5 and 15.
**Signature:** `def fizzBuzz(n: int) -> list[str]:`

**Expected approach and traps:**
- Loop 1..n; test 15 (or build "Fizz"+"Buzz") before 3 and 5. O(n).
- Traps: check order, 1-indexing, strings not ints.

**Results:** 27 pass, 0 fail of 27 graded answers. Table and code: [index.md](index.md).

**To verify for yourself:** run it against the pilot's hidden checker: `python3 -I bench/pilot/checker.py fizzbuzz <file.py>` (prints JSON with `pass`), or paste it into the original LeetCode problem.
