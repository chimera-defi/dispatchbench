Add percentage discount codes to the `inv` package in this repository. Work in the current directory.

1. In `inv/money.py`, add `apply_percent(cents: int, pct: int) -> int`. It returns `cents` reduced by `pct` percent, rounded half up to the nearest whole cent. For example, `apply_percent(1005, 10)` is 905, since 904.5 rounds up. `pct` must be an int from 0 to 100 inclusive; otherwise raise `ValueError`.
2. In `inv/store.py`:
   - Add `Store.add_code(code: str, pct: int) -> None`. Codes are case-insensitive. Adding a code that already exists, in any case, raises `ValueError`. An invalid `pct` raises `ValueError`.
   - Change `Store.total_cents` to `total_cents(self, code: str | None = None) -> int`. With a code, it applies that code's discount to the whole total, using `apply_percent`. An unknown code raises `KeyError`.
3. In `inv/cli.py`, support `total --code CODE`. It returns the discounted total formatted with `format_cents`. If the code is unknown, return exactly `unknown code: CODE`, echoing the code as the user typed it. Plain `total` is unchanged.
4. Add `tests/test_discount.py` with tests for the new behaviour.
5. Run `python3 -m pytest -q`; all tests must pass. Don't change existing behaviour.
